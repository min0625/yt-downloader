from __future__ import annotations

from yt_downloader.errors import InputError
from yt_downloader.services.audio import AudioDownloadService
from yt_downloader.services.base import DownloadRequest, DownloadService
from yt_downloader.services.subtitle import SubtitleDownloadService
from yt_downloader.services.video import VideoDownloadService

SERVICE_REGISTRY: dict[str, DownloadService] = {
    "video": VideoDownloadService(),
    "audio": AudioDownloadService(),
    "subtitle": SubtitleDownloadService(),
}


def get_service(mode: str) -> DownloadService:
    try:
        return SERVICE_REGISTRY[mode]
    except KeyError as exc:
        raise InputError(f"Unsupported download mode: {mode}") from exc


__all__ = ["DownloadRequest", "DownloadService", "get_service"]
