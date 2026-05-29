from __future__ import annotations

import importlib
from pathlib import Path

from yt_downloader.errors import DownloadError, InputError
from yt_downloader.services.base import DownloadRequest, _base_ydl_opts, _has_ffmpeg

AUDIO_FORMATS = ("mp3", "m4a")


class AudioDownloadService:
    def download(self, request: DownloadRequest) -> None:
        if request.format not in AUDIO_FORMATS:
            raise InputError(
                f"audio mode does not support format: {request.format}, use mp3 or m4a"
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

        ydl_opts: dict = {
            **_base_ydl_opts(),
            "noplaylist": True,
            "outtmpl": output_template,
        }

        if _has_ffmpeg():
            # With ffmpeg: download best audio then convert to target format
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": request.format,
                    "preferredquality": "192",
                }
            ]
        else:
            # Without ffmpeg: download in native format
            if request.format == "m4a":
                ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
            else:
                # mp3 streams are rare, fall back to m4a
                ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"

        try:
            with youtube_dl(ydl_opts) as ydl:
                result_code = ydl.download([request.url])
        except Exception as exc:
            raise DownloadError(f"Unknown error during audio download: {exc}") from exc

        if result_code != 0:
            raise DownloadError(f"Audio download failed, exit code: {result_code}")
