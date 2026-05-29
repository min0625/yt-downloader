from __future__ import annotations

import importlib
from pathlib import Path

from yt_downloader.errors import DownloadError, InputError
from yt_downloader.services.base import DownloadRequest, _base_ydl_opts, _has_ffmpeg

VIDEO_FORMATS = ("mp4", "webm")


def _build_merged_selector(video_format: str) -> str:
    if video_format == "mp4":
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    return "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best"


def _build_video_selector(video_format: str) -> str:
    return f"bestvideo[ext={video_format}]/bestvideo/best[ext={video_format}]/best"


def _build_audio_selector() -> str:
    return "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio"


class VideoDownloadService:
    def download(self, request: DownloadRequest) -> None:
        if request.format not in VIDEO_FORMATS:
            raise InputError(
                f"video mode does not support format: {request.format}, use mp4 or webm"
            )

        request.output_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(Path(request.output_dir) / "%(title)s.%(ext)s")
        video_output_template = str(
            Path(request.output_dir) / "%(title)s.video.%(ext)s"
        )
        audio_output_template = str(
            Path(request.output_dir) / "%(title)s.audio.%(ext)s"
        )

        try:
            yt_dlp_module = importlib.import_module("yt_dlp")
            youtube_dl = yt_dlp_module.YoutubeDL
        except ModuleNotFoundError as exc:
            raise DownloadError(
                "Missing yt-dlp dependency, run `uv sync --dev` first"
            ) from exc

        try:
            if _has_ffmpeg():
                with youtube_dl(
                    {
                        **_base_ydl_opts(),
                        "format": _build_merged_selector(request.format),
                        "outtmpl": output_template,
                        "noplaylist": True,
                        "merge_output_format": request.format,
                    }
                ) as ydl:
                    result_code = ydl.download([request.url])

                if result_code != 0:
                    raise DownloadError(
                        f"Video download failed, exit code: {result_code}"
                    )
            else:
                with youtube_dl(
                    {
                        **_base_ydl_opts(),
                        "format": _build_video_selector(request.format),
                        "outtmpl": video_output_template,
                        "noplaylist": True,
                    }
                ) as ydl:
                    video_result_code = ydl.download([request.url])

                if video_result_code != 0:
                    raise DownloadError(
                        f"Video stream download failed, exit code: {video_result_code}"
                    )

                with youtube_dl(
                    {
                        **_base_ydl_opts(),
                        "format": _build_audio_selector(),
                        "outtmpl": audio_output_template,
                        "noplaylist": True,
                    }
                ) as ydl:
                    audio_result_code = ydl.download([request.url])

                if audio_result_code != 0:
                    raise DownloadError(
                        f"Audio stream download failed, exit code: {audio_result_code}"
                    )
        except DownloadError:
            raise
        except Exception as exc:
            raise DownloadError(f"Video download failed: {exc}") from exc
