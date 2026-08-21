from unittest.mock import MagicMock, patch

from src.script_engine import SiteGroundScriptEngine


@patch("src.script_engine.bigquery.Client")
@patch("src.script_engine.genai.Client")
def test_fetch_telemetry_success(mock_genai_cls, mock_bq_class):
    """Test successful telemetry query with valid data returning structured hooks."""
    # Mock BigQuery Row behavior
    mock_row_1 = MagicMock()
    mock_row_1.hook_text = "Tired of slow hosting?"
    mock_row_1.avg_ctr = 0.054
    mock_row_1.conversion_rate = 0.12

    mock_row_2 = MagicMock()
    mock_row_2.hook_text = "Host with the absolute fastest."
    mock_row_2.avg_ctr = 0.041
    mock_row_2.conversion_rate = 0.09

    mock_query_job = MagicMock()
    mock_query_job.result.return_value = [mock_row_1, mock_row_2]

    mock_bq_client = MagicMock()
    mock_bq_client.query.return_value = mock_query_job

    # Under LIFO, patch 1 (bigquery.Client) maps to mock_bq_class,
    # and patch 2 (genai.Client) maps to mock_genai_cls.
    mock_bq_class.return_value = mock_bq_client

    engine = SiteGroundScriptEngine()
    telemetry = engine.fetch_pmax_telemetry("cloud_hosting")

    assert "Tired of slow hosting?" in telemetry
    assert "5.40%" in telemetry
    assert "Host with the absolute fastest." in telemetry


@patch("src.script_engine.bigquery.Client")
@patch("src.script_engine.genai.Client")
def test_fetch_telemetry_fallback(mock_genai_cls, mock_bq_class):
    """Test graceful fallback behavior when BigQuery query throws an exception."""
    mock_bq_client = MagicMock()
    mock_bq_client.query.side_effect = Exception("BigQuery connection timeout")
    mock_bq_class.return_value = mock_bq_client

    engine = SiteGroundScriptEngine()
    telemetry = engine.fetch_pmax_telemetry("cloud_hosting")

    # Assert fallback default hook guidelines are used
    assert "Default hook strategy" in telemetry
    assert "speed, security" in telemetry


@patch("src.script_engine.bigquery.Client")
@patch("src.script_engine.genai.Client")
def test_generate_campaign_script(mock_genai_cls, mock_bq_class):
    """Test that script engine successfully coordinates telemetry and structures a Gemini prompt."""
    mock_genai_client = MagicMock()
    mock_genai_cls.return_value = mock_genai_client

    # Mock script generation response
    mock_response = MagicMock()
    mock_response.text = (
        "[Script 1] Supercharged SiteGround hosting. [Script 2] Secure cloud nodes."
    )
    mock_genai_client.models.generate_content.return_value = mock_response

    # Mock BigQuery to trigger fallback safely
    mock_bq_client = MagicMock()
    mock_bq_client.query.side_effect = Exception("No BigQuery credentials configured")
    mock_bq_class.return_value = mock_bq_client

    engine = SiteGroundScriptEngine()
    scripts = engine.generate_scripts(
        prompt="Launch new fast cloud plans", category="cloud_hosting"
    )

    assert "[Script 1]" in scripts
    assert "SiteGround" in scripts
    mock_genai_client.models.generate_content.assert_called_once()
