from unittest.mock import MagicMock, patch

import pytest

from src.compositor import FFmpegCompositor


@patch("src.compositor.subprocess.run")
def test_compositor_missing_inputs(mock_run):
    """Test that compositor fails early if input files do not exist."""
    compositor = FFmpegCompositor()

    with pytest.raises(FileNotFoundError):
        compositor.stitch_screenshot(
            screenshot_path="non_existent_img.png",
            video_path="non_existent_video.mp4",
            output_path="output.mp4",
        )
    mock_run.assert_not_called()


@patch("src.compositor.os.path.exists")
@patch("src.compositor.subprocess.run")
def test_compositor_success(mock_run, mock_exists):
    """Test successful compilation command when inputs are found."""
    # Mock file existence checks
    mock_exists.return_value = True

    # Mock successful subprocess execution
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    compositor = FFmpegCompositor()
    output = compositor.stitch_screenshot(
        screenshot_path="mock_img.png",
        video_path="mock_video.mp4",
        output_path="output_campaign.mp4",
    )

    assert output == "output_campaign.mp4"
    mock_run.assert_called_once()

    # Assert correct ffmpeg filters were passed (alpha fade details)
    called_args = mock_run.call_args[0][0]
    assert "ffmpeg" in called_args
    # Check that filter_complex is joined or searched correctly
    assert any("fade=t=out" in arg for arg in called_args)
    assert any("overlay" in arg for arg in called_args)
