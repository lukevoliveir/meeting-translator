"""YouTube audio downloader using yt-dlp."""

import os
import subprocess
from pathlib import Path
from typing import Dict


def get_profiles_dir() -> Path:
    """Get the profiles directory, creating it if needed."""
    profiles_dir = Path.home() / ".meeting-translator" / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def get_audio_temp_dir() -> Path:
    """Get the temporary audio directory, creating it if needed."""
    temp_dir = Path.home() / ".meeting-translator" / "audio-temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_video_info(url: str) -> Dict[str, str]:
    """
    Fetch video title and duration from YouTube URL.

    Args:
        url: YouTube video URL

    Returns:
        Dictionary with 'title' and 'duration' keys

    Raises:
        ValueError: If URL is invalid or video is unavailable
        subprocess.CalledProcessError: If yt-dlp command fails
    """
    try:
        result = subprocess.run(
            ["yt-dlp", "--quiet", "--no-warnings", "-j", url],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            raise ValueError(f"Failed to fetch video info: {result.stderr}")

        import json
        data = json.loads(result.stdout)

        title = data.get("title", "Unknown")
        duration = data.get("duration", 0)

        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

        return {
            "title": title,
            "duration": duration_str,
            "duration_seconds": duration
        }

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid video data received: {e}")
    except subprocess.TimeoutExpired:
        raise ValueError("Request timed out. Check your internet connection.")
    except FileNotFoundError:
        raise ValueError("yt-dlp not found. Install it with: pip install yt-dlp")


def download_audio(url: str, output_filename: str) -> str:
    """
    Download audio from YouTube video and save as MP3.

    Args:
        url: YouTube video URL
        output_filename: Filename for the output audio (without extension)

    Returns:
        Path to the downloaded audio file

    Raises:
        ValueError: If URL is invalid or download fails
        subprocess.CalledProcessError: If yt-dlp command fails
    """
    temp_dir = get_audio_temp_dir()
    output_path = temp_dir / output_filename

    try:
        # Download audio as MP3
        subprocess.run(
            [
                "yt-dlp",
                "--quiet",
                "--no-warnings",
                "-x",
                "--audio-format", "mp3",
                "-o", str(output_path),
                url
            ],
            timeout=600,
            check=True
        )

        # Check if file was created
        if not output_path.exists():
            raise ValueError(f"Downloaded file not found at {output_path}")

        return str(output_path)

    except subprocess.TimeoutExpired:
        raise ValueError("Download timed out. The video might be too long.")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Download failed: {e}")
    except FileNotFoundError:
        raise ValueError("yt-dlp not found. Install it with: pip install yt-dlp")


def cleanup_temp_audio(filepath: str) -> None:
    """
    Delete a temporary audio file.

    Args:
        filepath: Path to the audio file to delete
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass
