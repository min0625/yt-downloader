# Conventions

## Language Policy

- Code text (docstrings, comments, error messages, UI labels): **English only**
- Documentation (README.md, AGENTS.md, MEMORY.md): **zh-TW**
- Exception: `README.md` may contain zh-TW prose

## Code Style

- Ruff lint selectors: E4, E7, E9, F, I, UP
- Type annotations required (checked by `ty`)
- Small focused functions; avoid over-abstraction
- No new dependencies unless necessary

## Git Commits

Conventional Commits (zh-Hant): `<type>[scope]: <description>`
Types: feat, fix, docs, refactor, test, chore, build, ci, perf, revert
Description: imperative, concise, single-change description

## Design Patterns

- Services inherit from `base.py` base class
- Errors centralized in `errors.py`
- ffmpeg: `_get_bundled_ffmpeg_exe()` → path; `_get_ffmpeg_location()` → parent dir (for yt-dlp `ffmpeg_location`)
- GUI progress: `queue.Queue` + progress_hook + asyncio poll (`asyncio.sleep(0.3)`) → `ui.log`
