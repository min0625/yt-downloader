from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    output_dir: Path
    format: str
    progress_hooks: tuple[Callable[[dict], None], ...] = field(default=())


class DownloadService(Protocol):
    def download(self, request: DownloadRequest) -> None: ...


def _get_bundled_ffmpeg_exe() -> str | None:
    """Return path to the bundled imageio-ffmpeg executable, or None if unavailable."""
    try:
        import imageio_ffmpeg  # type: ignore[import-untyped]

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _get_ffmpeg_location() -> str | None:
    """Return the ffmpeg directory for yt-dlp's ffmpeg_location option.

    Returns None when system ffmpeg is on PATH (yt-dlp auto-detects it).
    Returns the parent directory of the bundled binary when only imageio-ffmpeg
    is available, so yt-dlp can find ffmpeg there.
    """
    if shutil.which("ffmpeg") is not None:
        return None
    exe = _get_bundled_ffmpeg_exe()
    if exe is not None:
        return str(Path(exe).parent)
    return None


def _has_ffmpeg() -> bool:
    """Check whether ffmpeg is available via system install or bundled imageio-ffmpeg."""
    if shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None:
        return True
    return _get_bundled_ffmpeg_exe() is not None


def _base_ydl_opts() -> dict:
    """Return common yt-dlp options shared across all services."""
    opts: dict = {
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
    }
    ffmpeg_location = _get_ffmpeg_location()
    if ffmpeg_location is not None:
        opts["ffmpeg_location"] = ffmpeg_location
    return opts
