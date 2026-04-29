"""YouTube audio downloader using yt-dlp."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict


def _yt_dlp_bin() -> str:
    """Return the yt-dlp binary path, searching PATH and common user-install locations."""
    found = shutil.which("yt-dlp")
    if found:
        return found

    # sysconfig covers pip install --user on macOS (~/.../Python/3.x/bin) and Linux (~/.local/bin)
    import sysconfig
    for scheme in ("posix_user", "nt_user"):
        try:
            scripts_dir = sysconfig.get_path("scripts", scheme)
            if scripts_dir:
                candidate = Path(scripts_dir) / "yt-dlp"
                if candidate.exists():
                    return str(candidate)
        except (KeyError, TypeError):
            pass

    # Fallback: same directory as the current Python executable
    import sys
    adjacent = Path(sys.executable).parent / "yt-dlp"
    if adjacent.exists():
        return str(adjacent)

    raise FileNotFoundError(
        "yt-dlp binary not found. "
        "Run: pip install yt-dlp  (then restart the backend)"
    )


def get_profiles_dir() -> Path:
    profiles_dir = Path.home() / ".meeting-translator" / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def get_audio_temp_dir() -> Path:
    temp_dir = Path.home() / ".meeting-translator" / "audio-temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_video_info(url: str) -> Dict[str, str]:
    """Fetch video title and duration from a YouTube URL."""
    try:
        result = subprocess.run(
            [_yt_dlp_bin(), "--quiet", "--no-warnings", "-j", url],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            raise ValueError(f"Failed to fetch video info: {result.stderr.strip()}")

        data = json.loads(result.stdout)
        duration = data.get("duration", 0)
        minutes, seconds = divmod(int(duration), 60)
        duration_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

        return {
            "title": data.get("title", "Unknown"),
            "duration": duration_str,
            "duration_seconds": duration,
        }

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid video data received: {e}")
    except subprocess.TimeoutExpired:
        raise ValueError("Request timed out. Check your internet connection.")
    except FileNotFoundError as e:
        raise ValueError(str(e))


def download_audio(url: str, output_filename: str) -> str:
    """Download audio from a YouTube video and save as MP3."""
    temp_dir = get_audio_temp_dir()
    safe_name = output_filename.replace(" ", "_").replace(".", "_")
    output_path = temp_dir / f"{safe_name}.mp3"

    try:
        # android_vr client bypasses YouTube's SABR streaming restriction (403 on web clients)
        base_cmd = [
            _yt_dlp_bin(),
            "--quiet",
            "--no-warnings",
            "--extractor-args", "youtube:player_client=android_vr",
            "-x",
            "--audio-format", "mp3",
            "-o", str(output_path),
            url,
        ]
        result = subprocess.run(base_cmd, timeout=600, capture_output=True, text=True)

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, base_cmd, result.stderr)

        # yt-dlp may append a second .mp3 extension
        actual_path = output_path if output_path.exists() else Path(str(output_path) + ".mp3")
        if not actual_path.exists():
            raise ValueError(f"Downloaded file not found at {output_path}")

        return str(actual_path)

    except subprocess.TimeoutExpired:
        raise ValueError("Download timed out. The video might be too long.")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Download failed: {e}")
    except FileNotFoundError as e:
        raise ValueError(str(e))


def cleanup_temp_audio(filepath: str) -> None:
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass
