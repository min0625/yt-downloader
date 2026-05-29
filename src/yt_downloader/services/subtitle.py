from __future__ import annotations

import importlib
from pathlib import Path

from yt_downloader.errors import DownloadError, InputError
from yt_downloader.services.base import DownloadRequest, _base_ydl_opts, _has_ffmpeg

SUBTITLE_FORMATS = ("srt", "vtt")
# Default subtitle language priority order
DEFAULT_LANGS = ["zh-Hant", "zh-Hans", "en"]


class SubtitleDownloadService:
    def download(self, request: DownloadRequest) -> None:
        if request.format not in SUBTITLE_FORMATS:
            raise InputError(
                f"subtitle mode does not support format: {request.format}, use srt or vtt"
            )

        request.output_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(Path(request.output_dir) / "%(title)s.%(ext)s")

        try:
            yt_dlp_module = importlib.import_module("yt_dlp")
            youtube_dl = yt_dlp_module.YoutubeDL
        except ModuleNotFoundError as exc:
            raise DownloadError(
                "Missing yt-dlp dependency, run `uv sync --dev` first"
            ) from exc

        # srt requires ffmpeg for conversion; fall back to vtt without ffmpeg
        effective_format = request.format
        if request.format == "srt" and not _has_ffmpeg():
            effective_format = "vtt"

        ydl_opts: dict = {
            **_base_ydl_opts(),
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": DEFAULT_LANGS,
            "subtitlesformat": effective_format,
            "skip_download": True,
            "outtmpl": output_template,
            "noplaylist": True,
        }

        try:
            with youtube_dl(ydl_opts) as ydl:
                result_code = ydl.download([request.url])
        except Exception as exc:
            raise DownloadError(
                f"Unknown error during subtitle download: {exc}"
            ) from exc

        if result_code != 0:
            raise DownloadError(f"Subtitle download failed, exit code: {result_code}")
