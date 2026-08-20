# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
from collections.abc import AsyncIterator

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback
from app.studio_api import router as studio_router

load_dotenv()
setup_telemetry()
try:
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception as e:
    import logging

    logger = logging.getLogger(__name__)
    print(f"Cloud logging initialization fallback: {e}")
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from vertexai.agent_engines.templates.adk import AdkApp

    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name

    # Mount native A2A schema targets
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )

    # Attach the official platform reasoning engine mapping contract
    # This automatically registers both /api/reasoning_engine and /api/stream_reasoning_engine
    # compliant with Playgrounds and Gemini Enterprise (Agentspace)
    runtime = AdkApp(
        app=adk_app,
        session_service_builder=services.get_session_service,
        artifact_service_builder=services.get_artifact_service,
    )
    runtime.set_up()

    # Dynamically bind legacy endpoints directly to our FastAPI application router
    import inspect
    import json

    from fastapi import Request, encoders, responses

    operations = runtime.register_operations()
    streaming_methods = set(operations.get("stream", [])) | set(
        operations.get("async_stream", [])
    )
    sync_methods = set(operations.get("", [])) | set(operations.get("async", []))

    def resolve_method(class_method: str, *, streaming: bool):
        allowed = streaming_methods if streaming else sync_methods
        if class_method not in allowed:
            # Fallback to standard streaming_agent_run_with_events if not explicitly declared
            return runtime.streaming_agent_run_with_events
        return getattr(runtime, class_method)

    @app.post("/api/stream_reasoning_engine")
    async def stream_query(request: Request) -> responses.StreamingResponse:
        body = await request.json()
        class_method = body.get("class_method", "streaming_agent_run_with_events")
        method = resolve_method(class_method, streaming=True)

        # Safely extract and normalize complex input values
        input_args = body.get("input") or {}

        # AdkApp.streaming_agent_run_with_events strictly expects (self, request_json: str)
        # If input has request_json as a dict or string, normalize and supply it directly
        if method.__name__ == "streaming_agent_run_with_events":
            if "request_json" in input_args:
                req_val = input_args["request_json"]
                # If request_json value is already a dictionary, dump it back to string
                if isinstance(req_val, dict):
                    req_val = json.dumps(req_val)
                input_args = {"request_json": req_val}
            else:
                # If it's a simple text input query like {"query": "hello"} map it into standard request_json format
                query_text = input_args.get("query", "hello")
                mock_request_json = {
                    "message": {"role": "user", "parts": [{"text": query_text}]}
                }
                input_args = {"request_json": json.dumps(mock_request_json)}

        async def generator():
            async for event in method(**input_args):
                yield json.dumps(event) + "\n"

        return responses.StreamingResponse(
            content=generator(), media_type="application/json"
        )

    @app.post("/api/reasoning_engine")
    async def query(request: Request) -> responses.JSONResponse:
        body = await request.json()
        class_method = body.get("class_method", "agent_run")
        method = resolve_method(class_method, streaming=False)
        kwargs = body.get("input") or {}
        output = (
            await method(**kwargs)
            if inspect.iscoroutinefunction(method)
            else method(**kwargs)
        )
        return responses.JSONResponse(
            content=encoders.jsonable_encoder({"output": output})
        )

    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=False,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=["*"],
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "test-quick-project"
app.description = "API for interacting with the Agent test-quick-project"


app.include_router(studio_router)


@app.get("/")
@app.get("/studio")
@app.get("/ui")
@app.get("/index.html")
async def serve_studio_ui():
    """Serves the SiteGround AI Marketing Studio Web App."""
    index_path = os.path.join(AGENT_DIR, "index.html")
    return FileResponse(index_path)


@app.get("/media/{filename}")
async def serve_media_root(filename: str):
    """Serves media asset files (MP4, MP3, PNG) with dynamic generation fallback."""
    file_path = os.path.join(AGENT_DIR, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(AGENT_DIR, "media", filename)

    if not os.path.exists(file_path):
        if filename.startswith("asset_") or filename in ("slide.png", "sg_logo_badge.png", "gcp_cloud_badge.png"):
            from app.image_studio import generate_campaign_asset
            asset_type = "speed"
            if "error" in filename:
                asset_type = "error"
            elif "support" in filename or "trustpilot" in filename:
                asset_type = "support"
            elif "discount" in filename or "promo" in filename:
                asset_type = "discount"
            generate_campaign_asset(asset_type, "")
            file_path = os.path.join(AGENT_DIR, filename)
            if not os.path.exists(file_path):
                file_path = os.path.join(AGENT_DIR, "media", filename)
        elif filename.endswith(".mp4"):
            try:
                from app.video_renderer import render_marketing_video
                render_marketing_video(variant_id="variant_1", aspect_ratio="16:9", target_path=file_path)
            except Exception as e:
                print(f"Fallback video rendering: {e}")
        elif filename.endswith(".mp3"):
            try:
                from gtts import gTTS
                tts = gTTS(text="SiteGround Ultra-Fast Managed WordPress Hosting with Google Cloud Infrastructure.", lang="en")
                tts.save(file_path)
            except Exception as e:
                print(f"Fallback audio rendering: {e}")

    if os.path.exists(file_path):
        media_type = (
            "video/mp4"
            if filename.endswith(".mp4")
            else "audio/mpeg"
            if filename.endswith(".mp3")
            else "image/png"
        )
        return FileResponse(file_path, media_type=media_type)
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Media file not found")



@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
