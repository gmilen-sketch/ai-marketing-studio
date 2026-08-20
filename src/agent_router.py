import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from google import genai
from google.adk.workflow import BaseNode
from google.adk.workflow._errors import NodeInterruptedError
from google.cloud import bigquery
from google.genai import types


class SiteGroundVideoAgentNode(BaseNode):
    """
    Stateful ADK 2.0 Workflow Node for the SiteGround Video Production Pipeline.
    Integrates telemetry-driven scriptwriting, yields A2UI HITL consent events,
    triggers asynchronous video synthesis, and performs final campaign compilation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use private attributes (prefixed with '_') to avoid Pydantic field validation errors on BaseNode
        self._client = genai.Client()
        self._bq_client = bigquery.Client()
        self._script_model = "gemini-3.5-flash"
        self._video_model = "models/veo-3.2-creative-generate-002;backend_beyond"
        self._editor_model = "gemini-omni-flash-preview"

    def fetch_pmax_telemetry(self, campaign_category: str) -> str:
        """Fetch past top-performing campaign hooks from BigQuery."""
        try:
            query = """
                SELECT hook_text, avg_ctr, conversion_rate
                FROM `siteground_analytics.pmax_creative_telemetry`
                WHERE category = %s
                ORDER BY conversion_rate DESC LIMIT 3
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(None, "STRING", campaign_category)
                ]
            )
            query_job = self._bq_client.query(query, job_config=job_config)
            results = query_job.result()

            telemetry_lines = []
            for r in results:
                telemetry_lines.append(
                    f'- Hook: "{r.hook_text}" (CTR: {r.avg_ctr:.2%}, Conv: {r.conversion_rate:.2%})'
                )

            if not telemetry_lines:
                return "Default hook strategy: Focus on SiteGround speed, security, and 24/7 technical support."
            return "\n".join(telemetry_lines)

        except Exception:
            # Non-blocking degradation fallback
            return "Default hook strategy: Focus on SiteGround speed, security, and 24/7 technical support."

    async def execute(
        self, context: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Main graph execution loop yielding streaming status, consent events, and final results.
        """
        prompt = context.get("campaign_brief")
        category = context.get("category", "cloud_hosting")

        # 1. Yield initial progress events
        yield {
            "type": "node_info",
            "status": "fetching_telemetry",
            "message": "Reading BigQuery performance telemetry...",
        }
        telemetry_context = self.fetch_pmax_telemetry(category)

        # 2. Structure conversion-focused scripts
        yield {
            "type": "node_info",
            "status": "generating_script",
            "message": "Drafting multi-channel script variants...",
        }
        script_resp = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._script_model,
            contents=[
                f"Historical top performers:\n{telemetry_context}\n\nTask: Generate 3 horizontal ad scripts with SSML tags for: {prompt}"
            ],
        )

        # 3. HITL Consent Gate: Yield consent request event and check response state
        consent_state = context.get("hitl_consent_response")
        if not consent_state or "approved_script" not in consent_state:
            yield {
                "type": "hitl_consent_request",
                "node_name": self.name,
                "message": "Please review, edit, or approve the generated script storyboard.",
                "data": {
                    "generated_scripts": script_resp.text,
                    "schema_definition": {
                        "approved_script": {
                            "type": "string",
                            "description": "The script text to be voiced over and synthesized.",
                        }
                    },
                },
            }
            # Terminate current node loop execution with standard Interrupted exception
            raise NodeInterruptedError(
                "Awaiting explicit human approval on script storyboard."
            )

        approved_script = consent_state["approved_script"]
        yield {
            "type": "node_info",
            "status": "synthesizing_video",
            "message": "Initiating high-fidelity video generation via Veo 3.2...",
        }

        # 4. Asynchronous Video Generation
        video_op = await asyncio.to_thread(
            self._client.models.generate_videos,
            model=self._video_model,
            prompt=f"Cinematic server room animation, professional lighting, 24fps. Context: {approved_script}",
            config=types.GenerateVideosConfig(aspect_ratio="9:16", duration_seconds=8),
        )

        while not video_op.done:
            await asyncio.sleep(1)  # Faster polling during test simulation
            video_op = await asyncio.to_thread(self._client.operations.get, video_op)
            yield {
                "type": "node_info",
                "status": "synthesizing_video",
                "message": "Rendering 24fps cinematic b-roll...",
            }

        raw_video_uri = video_op.response.generated_videos[0].video.uri

        # 5. Yield final processed outputs
        yield {
            "type": "node_output",
            "output": {
                "approved_script": approved_script,
                "final_video_uri": raw_video_uri,
            },
        }
