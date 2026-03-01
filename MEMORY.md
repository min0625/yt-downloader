# MEMORY.md

Project memory index for YT Downloader. Keep this file concise and high-signal.

## Quick Facts

- Python CLI for downloading YouTube video/audio/subtitle.
- Package/environment workflow uses `uv` only.
- Repo currently uses `src/` layout: `src/yt_downloader/`.
- `pyproject.toml` includes minimal package metadata, `project.scripts` (`yt-downloader`), dev group (`ruff`, `ty`), and Ruff base rules.
- `.gitignore` excludes common Python/uv artifacts and keeps `downloads/` out of version control.
- `README.md` is the primary project entry document (zh-TW body with English section headings).
- `README.md` includes a disclaimer that the project is for educational/learning purposes only.
- `README.md` now uses two-layer disclaimer wording: a short notice near the top plus a detailed `## Disclaimer` section.

## Commands

- Install deps (include dev): `uv sync --dev`
- Tests: `uv run pytest`
- Format: `uv run ruff format`
- Lint: `uv run ruff check`
- Type check: `uv run ty check`
- Skills find: `npx skills find "<query>"`
- Skills add (project): `npx skills add <owner/repo@skill> -y`
- Skills list (project/global): `npx skills ls` / `npx skills ls -g`

## Architecture Notes

- CLI entrypoint is `src/yt_downloader/__main__.py` (current state: minimal `print("hello world")` skeleton).
- Packaging script command `yt-downloader` maps to `yt_downloader.__main__:main`.

## Pitfalls

- 文件檢查時先核對 `README.md` 與實際 repo 狀態；曾出現 `LICENSE` 已存在但文件仍寫「尚未定義授權／待補 LICENSE」的矛盾。
- 建立 PR 前先檢查 `pull_request_template.md` 與 `.github/PULL_REQUEST_TEMPLATE`；本 repo 目前沒有模板，需使用標準 PR 內文。
- 本 repo 的暫存下載輸出位於 `downloads/`，需透過 `.gitignore` 排除，避免媒體檔誤入版控。
- 進行 PR review 時先以 diff/changed files 為準，再比對 PR 內文摘要；PR 描述可能未即時反映後續 amend。
- 技能文件安全檢視需區分「教學示例」與「實際執行指令」：例如 `curl|sh`/`irm|iex` 或未參數化 SQL 可能出現在示例中，應標記為高風險樣式但不直接等同惡意。
- 目前 `uv run pytest` 會顯示 `collected 0 items`；在專案初始階段屬預期現況，review 時不應誤判為測試執行失敗。

## Decisions

- 文件（`README.md`、`AGENTS.md`、`MEMORY.md`、`memory/*.md`）預設使用 zh-TW。
- 程式註解預設使用 zh-TW；若檔案既有慣例明確為英文，沿用原慣例。
- 語系調整不可改動公開介面名稱（例如 CLI 旗標、對外 API 名稱）。
- Markdown 文件的章節標題（例如 `##`、`###`）以英文為主，本文語系可依文件政策維持 zh-TW。
- Git commit 訊息採用 Conventional Commits（zh-Hant）規範：`https://www.conventionalcommits.org/zh-hant/v1.0.0/`。

## Last Updated

- 2026-03-02: 重整 `README.md` 結構為 Overview/Requirements/Quick Start/Development Commands/Current Status/Roadmap，並保留現況導向描述（不誇大功能）。
- 2026-03-02: 修正 `MEMORY.md` 架構描述：CLI 目前為 `print("hello world")`，非 argparse 骨架。
- 2026-03-02: 在 `README.md` 開頭加入一句精簡免責聲明，形成「開頭短版＋章節完整版」雙層提示。
- 2026-03-02: 在 `README.md` 新增教育學習用途免責聲明，並提醒需遵守平台條款與相關法規。
- 2026-03-02: 對齊 `AGENTS.md` 與目前工作流，安裝開發相依統一為 `uv sync --dev`，並補上 `uv run yt-downloader` 常用執行指令。
- 2026-03-02: 精簡 MEMORY 結構與內容，移除重複流水帳，保留可重用命令、架構事實、review 陷阱與語系/提交慣例。
- 2026-03-02: 記錄目前初始狀態：`uv run pytest` 為 `collected 0 items` 屬預期，不視為測試失敗。
- 2026-03-02: 記錄已穩定的開發命令與 uv-only 工作流（`uv sync --dev`、`uv run ruff/ty/pytest`）。
