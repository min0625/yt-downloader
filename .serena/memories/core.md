# Core — YT Downloader

Python CLI + GUI tool for downloading YouTube video/audio/subtitles.
Repo uses `src/` layout: `src/yt_downloader/`.

## Source Map

- `src/yt_downloader/__main__.py` — entrypoint; mode detection (GUI vs CLI), arg parsing, service dispatch
- `src/yt_downloader/gui.py` — NiceGUI 3.x native window GUI
- `src/yt_downloader/services/` — download services: `video.py`, `audio.py`, `subtitle.py`, `base.py`
- `src/yt_downloader/errors.py` — `InputError`, `DownloadError`, `DownloaderError`
- `src/yt_downloader/_version.py` — version info (hatch-vcs); `__version__`, `__commit__`, `__commit_date__`, `__dirty__`
- `src/yt_downloader/_build_info.py` — generated at pack time (gitignored); read by `_version.py` as frozen fallback
- `scripts/generate_build_info.py` — generates `_build_info.py` before packaging
- `yt-downloader.spec` — PyInstaller spec (Windows: `console=False`, GUI-only)
- `tests/` — pytest tests (19 total)

## Invariants

- CLI flag interface: `--url` (required), `--output-dir` (default `downloads/`), `--mode` (video|audio|subtitle), `--format` (mp4|webm|mp3|m4a|srt|vtt), `--version`
- Mode detection: no args → GUI; args present → CLI (but frozen Windows exe always launches GUI)
- ffmpeg provided via `imageio-ffmpeg` (bundled); system ffmpeg used preferentially if available
- All code text (docstrings, comments, error messages, UI labels) must be English; docs use zh-TW
- `mem:tech_stack` — language, frameworks, tools
- `mem:conventions` — code/doc style rules
- `mem:suggested_commands` — dev and task commands
- `mem:task_completion` — commands to run when a task is done
