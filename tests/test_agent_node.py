from unittest.mock import MagicMock, patch

import pytest
from google.adk.workflow._errors import NodeInterruptedError

from src.agent_router import SiteGroundVideoAgentNode


@pytest.mark.asyncio
@patch("src.agent_router.genai.Client")
@patch("src.agent_router.bigquery.Client")
async def test_agent_node_consent_interruption(mock_bq_cls, mock_genai_cls):
    """Test that the node yields status events, then raises NodeInterruptedError for consent."""
    mock_genai_client = MagicMock()
    mock_genai_cls.return_value = mock_genai_client

    mock_resp = MagicMock()
    mock_resp.text = "Mock Script Storyboard Copy"
    mock_genai_client.models.generate_content.return_value = mock_resp

    # Instantiate node
    node = SiteGroundVideoAgentNode(name="siteground_routing_node")
    context = {
        "campaign_brief": "Build ultra-fast cloud server video",
        "category": "cloud_hosting",
    }

    events = []
    with pytest.raises(NodeInterruptedError):
        async for event in node.execute(context):
            events.append(event)

    # Check yielded events
    assert any(e.get("status") == "fetching_telemetry" for e in events)
    assert any(e.get("status") == "generating_script" for e in events)
    assert any(e.get("type") == "hitl_consent_request" for e in events)


@pytest.mark.asyncio
@patch("src.agent_router.genai.Client")
@patch("src.agent_router.bigquery.Client")
async def test_agent_node_resume_and_complete(mock_bq_cls, mock_genai_cls):
    """Test that the node executes to completion when consent is resolved in context."""
    mock_genai_client = MagicMock()
    mock_genai_cls.return_value = mock_genai_client

    # Mock script generation response
    mock_script_resp = MagicMock()
    mock_script_resp.text = "Approved Storyboard Copy"
    mock_genai_client.models.generate_content.return_value = mock_script_resp

    # Mock video generation response (operation polling mock)
    mock_video_op = MagicMock()
    mock_video_op.done = True
    mock_video_op.response.generated_videos = [MagicMock()]
    mock_video_op.response.generated_videos[
        0
    ].video.uri = "gs://siteground/assets/broll.mp4"
    mock_genai_client.models.generate_videos.return_value = mock_video_op

    node = SiteGroundVideoAgentNode(name="siteground_routing_node")
    context = {
        "campaign_brief": "Build ultra-fast cloud server video",
        "category": "cloud_hosting",
        "hitl_consent_response": {"approved_script": "The approved script copy!"},
    }

    events = []
    async for event in node.execute(context):
        events.append(event)

    assert any(e.get("status") == "synthesizing_video" for e in events)
    assert any(e.get("type") == "node_output" for e in events)

    output_event = next(e for e in events if e.get("type") == "node_output")
    assert (
        output_event["output"]["final_video_uri"] == "gs://siteground/assets/broll.mp4"
    )
    assert output_event["output"]["approved_script"] == "The approved script copy!"
