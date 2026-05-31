from __future__ import annotations

import asyncio
import json
import queue
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from nicegui import app, run, ui

from yt_downloader._version import format_version_compact
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

        with ui.row().classes("w-full gap-2 items-end"):
            output_dir_input = ui.input(
                label="Output Directory",
                value=str(Path.home() / "Downloads"),
            ).classes("flex-1")
            pick_dir_btn = ui.button("Browse...")

        download_btn = ui.button("Start Download").classes("w-full")

        log_lines: list[str] = []
        log = ui.log(max_lines=200).classes("w-full h-48 font-mono text-sm yt-dl-log")

        # Make log text selectable via CSS override
        ui.add_css(".yt-dl-log * { user-select: text !important; cursor: text; }")

        async def on_copy_log() -> None:
            """Copy all log lines to clipboard."""
            content = "\n".join(log_lines)
            await ui.run_javascript(
                f"navigator.clipboard.writeText({json.dumps(content)})",
                timeout=5.0,
            )
            ui.notify("Copied to clipboard", type="positive")

        async def on_export_log() -> None:
            """Export log via native save dialog."""
            if not log_lines:
                ui.notify("No log content to export", type="warning")
                return
            window = app.native.main_window
            if window is None:
                ui.notify("Unable to open save dialog", type="warning")
                return
            try:
                # 30 = webview.FileDialog.SAVE (integer literal avoids NiceGUI proxy type issue)
                result = await getattr(window, "create_file_dialog")(
                    30,
                    save_filename="yt-downloader-log.txt",
                    file_types=("Text Files (*.txt)", "All Files (*.*)"),
                )
                if not result:
                    return
                save_path = result[0]
                content = "\n".join(log_lines)

                def write_file() -> None:
                    Path(save_path).write_text(content, encoding="utf-8")

                await run.io_bound(write_file)
                ui.notify(f"Log saved to {save_path}", type="positive")
            except Exception as exc:
                ui.notify(f"Unable to save log: {exc}", type="warning")

        def push_log(msg: str) -> None:
            """Push a message to the log UI and internal buffer."""
            log.push(msg)
            log_lines.append(msg)

        with ui.row().classes("w-full gap-2 justify-end"):
            ui.button("Copy Log", on_click=on_copy_log).props(
                "flat dense icon=content_copy"
            )
            ui.button("Export Log", on_click=on_export_log).props(
                "flat dense icon=download"
            )

        ui.label(format_version_compact()).classes(
            "text-xs text-gray-400 self-end select-text"
        )

    def on_mode_change(e: ValueChangeEventArguments) -> None:
        options = FORMAT_OPTIONS.get(e.value, [])
        format_select.options = options
        format_select.value = options[0] if options else None
        format_select.update()

    mode_select.on_value_change(on_mode_change)

    async def on_pick_folder() -> None:
        """Open native folder picker and update output directory input."""
        try:
            window = app.native.main_window
            if window is None:
                ui.notify("Unable to open folder picker", type="warning")
                return
            current = (output_dir_input.value or "").strip() or str(
                Path.home() / "Downloads"
            )
            # 20 = webview.FileDialog.FOLDER (integer literal avoids NiceGUI proxy type issue)
            # WindowProxy dynamically proxies pywebview; use getattr to satisfy the type checker
            result = await getattr(window, "create_file_dialog")(
                20,
                directory=current,
                allow_multiple=False,
            )
            if result:
                output_dir_input.value = result[0]
        except Exception as exc:
            ui.notify(f"Unable to open folder picker: {exc}", type="warning")

    pick_dir_btn.on_click(on_pick_folder)

    async def on_download_click() -> None:
        url = (url_input.value or "").strip()
        if not url:
            ui.notify("Please enter a YouTube URL", type="warning")
            return

        mode = mode_select.value or "video"
        fmt = format_select.value or FORMAT_OPTIONS[mode][0]
        output_dir = (output_dir_input.value or str(Path.home() / "Downloads")).strip()

        download_btn.props("disabled")
        started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        push_log(f"[{started_at}] ▶ Starting download")
        push_log(f"  version    : {format_version_compact()}")
        push_log(f"  url        : {url}")
        push_log(f"  mode       : {mode}")
        push_log(f"  format     : {fmt}")
        push_log(f"  output_dir : {output_dir}")

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
                push_log(msg_queue.get_nowait())

        # Flush remaining messages
        while not msg_queue.empty():
            push_log(msg_queue.get_nowait())

        error: str | None = download_future.result()

        if error:
            push_log(f"\u2717 Error: {error}")
            ui.notify("Download failed", type="negative")
        else:
            push_log("\u2713 Download complete!")
            ui.notify("Download complete!", type="positive")

        download_btn.props(remove="disabled")

    download_btn.on_click(on_download_click)


@ui.page("/")
def _index() -> None:
    _build_ui()


def launch() -> None:
    """Launch GUI mode (native window)."""
    if sys.platform == "win32":
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    ui.run(
        native=True,
        title=f"YT Downloader {format_version_compact()}",
        host="127.0.0.1",
        port=8765,
        reload=False,
        show_welcome_message=False,
    )
