from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    output_dir: Path
    format: str


class DownloadService(Protocol):
    def download(self, request: DownloadRequest) -> None: ...


def _has_ffmpeg() -> bool:
    """Check whether ffmpeg and ffprobe are installed on the system."""
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def _base_ydl_opts() -> dict:
    """Return common yt-dlp options shared across all services."""
    return {
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
    }
