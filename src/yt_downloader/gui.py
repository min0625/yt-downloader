from __future__ import annotations

import asyncio
import queue
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from nicegui import run, ui

from yt_downloader.errors import DownloaderError, DownloadError, InputError
from yt_downloader.services import DownloadRequest
from yt_downloader.services.base import _has_ffmpeg

if TYPE_CHECKING:
    from nicegui.events import ValueChangeEventArguments

# Allowed formats per mode
FORMAT_OPTIONS: dict[str, list[str]] = {
    "video": ["mp4", "webm"],
    "audio": ["mp3", "m4a"],
    "subtitle": ["srt", "vtt"],
}
MODES = list(FORMAT_OPTIONS.keys())


def _build_ui() -> None:
    """Build main page UI components."""

    with ui.column().classes("w-full max-w-2xl mx-auto p-6 gap-4"):
        ui.label("YT Downloader").classes("text-3xl font-bold")

        url_input = ui.input(
            label="YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
        ).classes("w-full")

        with ui.row().classes("w-full gap-4"):
            mode_select = ui.select(
                options=MODES,
                value="video",
                label="Download Mode",
            ).classes("flex-1")

            format_select = ui.select(
                options=FORMAT_OPTIONS["video"],
                value="mp4",
                label="Output Format",
            ).classes("flex-1")

        output_dir_input = ui.input(
            label="Output Directory",
            value="downloads/",
        ).classes("w-full")

        download_btn = ui.button("Start Download").classes("w-full")

        log = ui.log(max_lines=200).classes("w-full h-48 font-mono text-sm")

    def on_mode_change(e: ValueChangeEventArguments) -> None:
        options = FORMAT_OPTIONS.get(e.value, [])
        format_select.options = options
        format_select.value = options[0] if options else None
        format_select.update()

    mode_select.on_value_change(on_mode_change)

    async def on_download_click() -> None:
        url = (url_input.value or "").strip()
        if not url:
            ui.notify("Please enter a YouTube URL", type="warning")
            return

        mode = mode_select.value or "video"
        fmt = format_select.value or FORMAT_OPTIONS[mode][0]
        output_dir = (output_dir_input.value or "downloads/").strip()

        download_btn.props("disabled")
        log.push("\u25b6 Starting download...")

        request = DownloadRequest(
            url=url,
            output_dir=Path(output_dir),
            format=fmt,
        )

        # Use Queue to collect yt-dlp progress messages
        msg_queue: queue.Queue[str] = queue.Queue()

        def progress_hook(d: dict) -> None:
            status = d.get("status", "")
            if status == "downloading":
                percent = (d.get("_percent_str") or "").strip()
                speed = (d.get("_speed_str") or "").strip()
                eta = (d.get("_eta_str") or "").strip()
                msg_queue.put(f"  Downloading {percent}  Speed {speed}  ETA {eta}")
            elif status == "finished":
                msg_queue.put("  Stream download complete, post-processing...")

        def run_download() -> str | None:
            """Run download in a background thread, return error string or None."""
            try:
                # Inject progress hook into service (video/audio/subtitle all go through yt-dlp)
                _inject_progress_hook(request, mode, fmt, progress_hook)
                return None
            except DownloaderError as exc:
                return str(exc)

        # Start download (io_bound runs in thread pool)
        download_task = run.io_bound(run_download)
        download_future: asyncio.Future[str | None] = asyncio.ensure_future(
            download_task
        )

        # Poll progress messages every 300ms until download completes
        while not download_future.done():
            await asyncio.sleep(0.3)
            while not msg_queue.empty():
                log.push(msg_queue.get_nowait())

        # Flush remaining messages
        while not msg_queue.empty():
            log.push(msg_queue.get_nowait())

        error: str | None = download_future.result()

        if error:
            log.push(f"\u2717 Error: {error}")
            ui.notify("Download failed", type="negative")
        else:
            log.push("\u2713 Download complete!")
            ui.notify("Download complete!", type="positive")

        download_btn.props(remove="disabled")

    download_btn.on_click(on_download_click)


def _inject_progress_hook(
    request: DownloadRequest,
    mode: str,
    fmt: str,
    hook: object,
) -> None:
    """Call yt-dlp directly and inject the progress hook without modifying the service interface."""
    import importlib

    try:
        yt_dlp_module = importlib.import_module("yt_dlp")
        YoutubeDL = yt_dlp_module.YoutubeDL  # noqa: N806
    except ModuleNotFoundError as exc:
        raise DownloadError(
            "Missing yt-dlp dependency, run `uv sync --dev` first"
        ) from exc

    has_ffmpeg = _has_ffmpeg()
    output_template = str(request.output_dir / "%(title)s.%(ext)s")
    request.output_dir.mkdir(parents=True, exist_ok=True)

    if mode == "video":
        from yt_downloader.services.video import (  # noqa: PLC0415
            VIDEO_FORMATS,
            _build_audio_selector,
            _build_merged_selector,
            _build_video_selector,
        )

        if fmt not in VIDEO_FORMATS:
            raise InputError(
                f"video mode does not support format: {fmt}, use mp4 or webm"
            )

        if has_ffmpeg:
            ydl_opts = {
                "format": _build_merged_selector(fmt),
                "outtmpl": output_template,
                "noplaylist": True,
                "merge_output_format": fmt,
                "progress_hooks": [hook],
            }
        else:
            video_tmpl = str(request.output_dir / "%(title)s.video.%(ext)s")
            audio_tmpl = str(request.output_dir / "%(title)s.audio.%(ext)s")
            # Without ffmpeg: download video stream first
            ydl_opts = {
                "format": _build_video_selector(fmt),
                "outtmpl": video_tmpl,
                "noplaylist": True,
                "progress_hooks": [hook],
            }
            with YoutubeDL(ydl_opts) as ydl:
                rc = ydl.download([request.url])
            if rc != 0:
                raise DownloadError(f"Video stream download failed, exit code: {rc}")
            # Download audio stream
            ydl_opts = {
                "format": _build_audio_selector(),
                "outtmpl": audio_tmpl,
                "noplaylist": True,
                "progress_hooks": [hook],
            }
            with YoutubeDL(ydl_opts) as ydl:
                rc = ydl.download([request.url])
            if rc != 0:
                raise DownloadError(f"Audio stream download failed, exit code: {rc}")
            return

    elif mode == "audio":
        from yt_downloader.services.audio import AUDIO_FORMATS  # noqa: PLC0415

        if fmt not in AUDIO_FORMATS:
            raise InputError(
                f"audio mode does not support format: {fmt}, use mp3 or m4a"
            )

        if has_ffmpeg:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "noplaylist": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": fmt,
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [hook],
            }
        else:
            ydl_opts = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "outtmpl": output_template,
                "noplaylist": True,
                "progress_hooks": [hook],
            }

    elif mode == "subtitle":
        from yt_downloader.services.subtitle import (  # noqa: PLC0415
            DEFAULT_LANGS,
            SUBTITLE_FORMATS,
        )

        if fmt not in SUBTITLE_FORMATS:
            raise InputError(
                f"subtitle mode does not support format: {fmt}, use srt or vtt"
            )

        effective_format = fmt if has_ffmpeg or fmt == "vtt" else "vtt"
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": DEFAULT_LANGS,
            "subtitlesformat": effective_format,
            "skip_download": True,
            "outtmpl": output_template,
            "noplaylist": True,
            "progress_hooks": [hook],
        }
    else:
        raise InputError(f"Unsupported download mode: {mode}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            rc = ydl.download([request.url])
    except Exception as exc:
        raise DownloadError(f"Unknown error during download: {exc}") from exc

    if rc != 0:
        raise DownloadError(f"Download failed, exit code: {rc}")


@ui.page("/")
def _index() -> None:
    _build_ui()


def launch() -> None:
    """Launch GUI mode (native window)."""
    # Windows: when packaged as an executable, double-clicking opens a console window;
    # hide it in GUI mode
    if sys.platform == "win32":
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE

    ui.run(
        native=True,
        title="YT Downloader",
        host="127.0.0.1",
        port=8765,
        reload=False,
        show_welcome_message=False,
    )
