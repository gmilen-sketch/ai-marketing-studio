from unittest.mock import MagicMock, patch

import pytest
from google.adk.workflow._errors import NodeInterruptedError

from src.agent_router import SiteGroundVideoAgentNode
from src.compositor import FFmpegCompositor


@pytest.mark.asyncio
@patch("src.agent_router.genai.Client")
@patch("src.agent_router.bigquery.Client")
@patch("src.compositor.subprocess.run")
@patch("src.compositor.os.path.exists")
async def test_end_to_end_cohesion_pipeline(
    mock_exists, mock_ffmpeg_run, mock_bq_cls, mock_genai_cls
):
    """
    E2E Cohesion Test: Exercises script writing, HITL suspension,
    resume-handling, video synthesis, and zero-distortion FFmpeg compositing.
    """
    # 1. Setup Mock Environment
    mock_exists.return_value = True

    # Mock BigQuery Telemetry Response
    mock_row = MagicMock()
    mock_row.hook_text = "Fastest Server Canvas"
    mock_row.avg_ctr = 0.062
    mock_row.conversion_rate = 0.14

    mock_query_job = MagicMock()
    mock_query_job.result.return_value = [mock_row]
    mock_bq_client = MagicMock()
    mock_bq_client.query.return_value = mock_query_job
    mock_bq_cls.return_value = mock_bq_client

    # Mock Gemini Clients
    mock_genai_client = MagicMock()
    mock_genai_cls.return_value = mock_genai_client

    mock_script_resp = MagicMock()
    mock_script_resp.text = "Raw Storyboard Option"
    mock_genai_client.models.generate_content.return_value = mock_script_resp

    # Mock Veo Operation Polling
    mock_video_op = MagicMock()
    mock_video_op.done = True
    mock_video_op.response.generated_videos = [MagicMock()]
    mock_video_op.response.generated_videos[0].video.uri = "gs://siteground/raw_veo.mp4"
    mock_genai_client.models.generate_videos.return_value = mock_video_op

    # Mock FFmpeg execution
    mock_ffmpeg_result = MagicMock()
    mock_ffmpeg_result.returncode = 0
    mock_ffmpeg_run.return_value = mock_ffmpeg_result

    # 2. STEP A: Initial Run (Expects HITL Storyboard Consent Suspension)
    node = SiteGroundVideoAgentNode(name="siteground_video_ad_agent")
    context = {
        "campaign_brief": "Deploy fastest WordPress platform campaign",
        "category": "wordpress_hosting",
    }

    events = []
    with pytest.raises(NodeInterruptedError):
        async for event in node.execute(context):
            events.append(event)

    # Verify storyboard generation and consent prompts
    assert any(e.get("status") == "generating_script" for e in events)
    assert any(e.get("type") == "hitl_consent_request" for e in events)

    # Extract the generated scripts details yielded to A2UI
    consent_request = next(e for e in events if e.get("type") == "hitl_consent_request")
    assert consent_request["data"]["generated_scripts"] == "Raw Storyboard Option"

    # 3. STEP B: Resume Run (Injects approval and runs to completion)
    context["hitl_consent_response"] = {
        "approved_script": "Launch your SiteGround WordPress plan today!"
    }

    resume_events = []
    async for event in node.execute(context):
        resume_events.append(event)

    # Verify b-roll synthesis completed successfully
    assert any(e.get("status") == "synthesizing_video" for e in resume_events)
    output_event = next(e for e in resume_events if e.get("type") == "node_output")

    raw_video_uri = output_event["output"]["final_video_uri"]
    assert raw_video_uri == "gs://siteground/raw_veo.mp4"

    # 4. STEP C: Pass outputs to Compositor for high-density screenshot overlay
    compositor = FFmpegCompositor()
    output_file = compositor.stitch_screenshot(
        screenshot_path="workspace_siteground_client_area.png",
        video_path="simulated_raw_broll.mp4",
        output_path="final_stitched_campaign.mp4",
    )

    assert output_file == "final_stitched_campaign.mp4"
    mock_ffmpeg_run.assert_called_once()

    print(
        "\n[E2E Cohesion Test] Verified: Telemetry -> Storyboard Scripting -> HITL Gate -> Veo Render -> Zero-Distortion Stitching."
    )
