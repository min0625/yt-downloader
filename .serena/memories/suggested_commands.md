# Suggested Commands

All commands run from the project root on Windows (PowerShell or Git Bash).

## Setup

```
mise install              # install tool versions (Python, Node, etc.)
mise run sync             # uv sync --dev --frozen + pre-commit install
```

## Run

```
uv run yt-downloader                                                    # GUI mode
uv run yt-downloader --url "..." --mode video --format mp4             # CLI mode
```

## Dev Workflow

```
mise run check            # format + lint fix + ty type-check + test + pack (all checks)
uv run pytest             # tests only (19 tests, all should pass)
uv run pre-commit run --all-files   # or: mise run pre-commit
mise run pack             # generate_build_info.py + pyinstaller
```

## Windows-Specific Notes

- Use `uv run <cmd>` not `python -m <cmd>`
- Git Bash preferred for shell scripts; PowerShell also works
