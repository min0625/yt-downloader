# Tech Stack

- Python 3.14+; `requires-python = ">=3.14"` in pyproject.toml
- Build system: `hatchling` + `hatch-vcs` (version from git tags)
- Package manager: `uv` only — never use `pip` or `python -m pip`
- Dev environment: `mise` (see `mise.toml`); manages Node.js + uv versions

## Runtime Dependencies

- `yt-dlp` — download engine
- `nicegui[native]>=3.12.1` — GUI (pywebview-based native window)
- `imageio-ffmpeg>=0.5.1` — bundled ffmpeg binary

## Dev Dependencies

- `pytest` — testing
- `ruff` — formatting + lint (select: E4, E7, E9, F, I, UP)
- `ty` — type checking
- `pyinstaller` — packaging
- `pre-commit` — git hooks

## Packaging

PyInstaller spec `yt-downloader.spec`; Windows `console=False` (GUI-only exe).
macOS supports both GUI and CLI (double-click `.app` or terminal with args).
