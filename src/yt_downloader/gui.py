from __future__ import annotations

import asyncio
import queue
from pathlib import Path
from typing import TYPE_CHECKING

from nicegui import run, ui

from yt_downloader._version import (
    __commit__,
    __commit_date__,
    __dirty__,
    __ref__,
    __version__,
)
from yt_downloader.errors import DownloaderError
from yt_downloader.services import DownloadRequest, get_service

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

        _commit_date_short = (
            __commit_date__[:10] if len(__commit_date__) >= 10 else __commit_date__
        )
        _dirty_mark = "-dirty" if __dirty__ else ""
        ui.label(
            f"v{__version__}{_dirty_mark}  {__ref__}@{__commit__}  {_commit_date_short}"
        ).classes("text-xs text-gray-400 self-end")

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

        request = DownloadRequest(
            url=url,
            output_dir=Path(output_dir),
            format=fmt,
            progress_hooks=(progress_hook,),
        )

        def run_download() -> str | None:
            """Run download in a background thread, return error string or None."""
            try:
                get_service(mode).download(request)
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


@ui.page("/")
def _index() -> None:
    _build_ui()


def launch() -> None:
    """Launch GUI mode (native window)."""
    ui.run(
        native=True,
        title="YT Downloader",
        host="127.0.0.1",
        port=8765,
        reload=False,
        show_welcome_message=False,
    )
