import os
import subprocess


class FFmpegCompositor:
    """
    FFmpeg media processing wrapper.
    Safely composites high-density PNG screenshots of the SiteGround Client Area
    over raw generated Veo 3.2 video assets with alpha crossfades to avoid text distortion.
    """

    def stitch_screenshot(
        self, screenshot_path: str, video_path: str, output_path: str
    ) -> str:
        """
        Overlay static UI image over generated b-roll.
        Uses a custom scale, padding, and out-fading transition filter.
        """
        # Early-fail checks to meet test expectations
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found at path: {screenshot_path}")
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"B-roll video not found at path: {video_path}")

        # The composite pipeline parameters
        # scale to 1080:1920, pad, overlay first 3 seconds, fade out transition over 0.8 seconds
        command = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            "3",
            "-i",
            screenshot_path,
            "-i",
            video_path,
            "-filter_complex",
            "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fade=t=out:st=2.2:d=0.8[ui]; "
            "[ui][1:v]overlay=0:0:format=auto[v]",
            "-map",
            "[v]",
            "-map",
            "1:a?",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
            output_path,
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg pipeline execution failed: {result.stderr}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg call failed with error: {e.stderr}") from None
