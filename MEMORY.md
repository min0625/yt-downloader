# MEMORY.md

Project memory index for YT Downloader. Keep this file concise and high-signal.

## Quick Facts

- Python CLI + GUI 工具，用於下載 YouTube 影片／音訊／字幕。
- Package/environment workflow uses `uv` only；開發環境版本管理使用 `mise`（見 `mise.toml`）。
- Repo uses `src/` layout: `src/yt_downloader/`。
- `pyproject.toml`：dependencies 含 `nicegui[native]`、`yt-dlp`；dev 含 `pyinstaller`、`pytest`、`ruff`、`ty`。
- CLI 參數介面：`--url`（必要）、`--output-dir`（預設 `downloads/`）、`--mode`（`video|audio|subtitle`）、`--format`（`mp4|webm|mp3|m4a|srt|vtt`）。
- 模式偵測：`main()` 判斷 `sys.argv[1:]` 是否為空；無引數 → GUI，有引數 → CLI。
- GUI 模式以 NiceGUI 3.x 實作（`src/yt_downloader/gui.py`）：原生視窗（pywebview），port 8765，含即時進度顯示（queue + asyncio 輪詢）。
- 下載服務：`video`、`audio`、`subtitle` 均已實作真實下載邏輯（非 stub）。
  - `video`：有 ffmpeg → 合併單檔；無 ffmpeg → 分離串流（`.video.*` + `.audio.*`）。
  - `audio`：有 ffmpeg → `FFmpegExtractAudio` 轉換；無 ffmpeg → 原生 m4a。
  - `subtitle`：優先語言 `["zh-Hant", "zh-Hans", "en"]`，有 ffmpeg 支援 srt，無 ffmpeg 退回 vtt。
- 測試基準：`uv run pytest` 收集 17 個測試並全部通過。
- `README.md` 為主要專案文件（zh-TW）；含免責聲明（開頭短版 + `## Disclaimer` 章節）。
- `SUBTASKS.md` 用於集中管理可執行子任務清單（目前 Task 1–7 全部完成）。
- 版本機制：`hatch-vcs` 從 git tag 決定版本；`_version.py` 提供 `__version__`、`__commit__`、`__ref__`、`__build_date__`、`__build_time__`、`__dirty__`；CLI `--version` 旗標；GUI 底部顯示版本標籤（含 dirty mark）；打包前執行 `scripts/generate_build_info.py`（產出 BUILD_VERSION/COMMIT/BRANCH/DATE/TIME/DIRTY）。

## Commands

- 初始環境設置：`mise install` 後執行 `mise run sync`
- Sync（安裝依賴 + 設定 git hooks）: `mise run sync`（執行 `uv sync --dev && uv run pre-commit install`）
- Run all checks（格式化 + lint fix + ty 型別檢查 + 測試）: `mise run check`
- Full CI check（check + pack，發版前用）: `mise run ci`
- Run pre-commit on all files: `uv run pre-commit run --all-files` or `mise run pre-commit`
- Run GUI: `uv run yt-downloader`（無引數）
- Run CLI: `uv run yt-downloader --url "..." --mode video --format mp4`
- Pack: `uv run pyinstaller yt-downloader.spec`
- 安裝 `ffmpeg` 後請重開終端，確認：`ffmpeg -version`、`ffprobe -version`
- Skills find: `npx skills find "<query>"`
- Skills add (project): `npx skills add <owner/repo@skill> -y`

## Architecture Notes

- CLI entrypoint is `src/yt_downloader/__main__.py`，負責模式偵測（GUI vs CLI）、參數解析與 service 分派，下載細節下放至 `src/yt_downloader/services/`。
- GUI entrypoint 是 `src/yt_downloader/gui.py`，透過 `launch()` 以 NiceGUI native 模式啟動。
- 進度顯示：GUI 透過 `queue.Queue` + progress_hook + asyncio 輪詢 (`asyncio.sleep(0.3)`) 更新 `ui.log`。
- Packaging script command `yt-downloader` maps to `yt_downloader.__main__:main`.
- 錯誤型別集中於 `src/yt_downloader/errors.py`（`InputError`、`DownloadError`、`DownloaderError`）。

## Pitfalls

- 文件檢查時先核對 `README.md` 與實際 repo 狀態；曾出現 `LICENSE` 已存在但文件仍寫「尚未定義授權／待補 LICENSE」的矛盾。
- 建立 PR 前先檢查 `pull_request_template.md` 與 `.github/PULL_REQUEST_TEMPLATE`；本 repo 目前沒有模板，需使用標準 PR 內文。
- 本 repo 的暫存下載輸出位於 `downloads/`，需透過 `.gitignore` 排除，避免媒體檔誤入版控。
- 進行 PR review 時先以 diff/changed files 為準，再比對 PR 內文摘要；PR 描述可能未即時反映後續 amend。
- 技能文件安全檢視需區分「教學示例」與「實際執行指令」：例如 `curl|sh`/`irm|iex` 或未參數化 SQL 可能出現在示例中，應標記為高風險樣式但不直接等同惡意。
- 若需驗證目前 CLI 介面、分派與所有服務回歸，先執行 `uv run pytest tests/`；目前基準為 `collected 17 items` 並應全部通過。
- 若 `video` 產出為 `.video.*` + `.audio.*` 兩檔，代表目前走到無 `ffmpeg` 的 fallback 路徑；若要單檔輸出，先確認 `where ffmpeg` / `where ffprobe`。
- GUI 模式使用 NiceGUI native（pywebview）；若 pywebview 初始化失敗，請確認 `nicegui[native]` 已安裝（`uv sync --dev`）。
- `gui.py` 的 `_inject_progress_hook` 直接呼叫 yt-dlp（不透過 service），以便注入 `progress_hooks`；若 service 邏輯更新，需同步確認此函式的格式選擇邏輯仍對齊。
- 打包指令：`uv run pyinstaller yt-downloader.spec`；輸出在 `dist/yt-downloader.exe`（Windows）或 `dist/yt-downloader` + `dist/YT Downloader.app`（macOS）。
- Windows 打包後雙擊 GUI 模式時，`gui.py launch()` 會以 `ctypes.windll.user32.ShowWindow(hwnd, 0)` 隱藏 console 視窗。
- pywebview 模組名稱為 `webview`（非 `pywebview`），`webview/__pyinstaller/hook-webview.py` 提供內建 PyInstaller hook，spec 已透過 `hookspath` 引用。
- **PyInstaller + pywebview multiprocessing 陷阱**：pywebview 在 Windows 使用 `multiprocessing` spawn 子程序，子程序會帶 `--multiprocessing-fork parent_pid=... pipe_handle=...` 參數重新執行 exe，導致 `sys.argv[1:]` 非空進入 CLI 模式、argparse 報錯。修復方法：在 `if __name__ == '__main__':` 的第一行加 `multiprocessing.freeze_support()`。
- pytest 在本 repo 需明確指定 `tests/` 目錄（`uv run pytest tests/ -q`），直接執行 `uv run pytest -q` 可能遇到路徑問題。

## Decisions

- 文件（`README.md`、`AGENTS.md`、`MEMORY.md`、`memory/*.md`）預設使用 zh-TW；`README.md` 可保留 zh-TW。
- 程式碼（`.py`、`.toml` 等）內的所有文字（docstring、comment、error message、UI label）**統一使用英文**；`README.md` 例外。
- 語系調整不可改動公開介面名稱（例如 CLI 旗標、對外 API 名稱）。
- Markdown 文件的章節標題（例如 `##`、`###`）以英文為主，本文語系可依文件政策維持 zh-TW。
- Git commit 訊息採用 Conventional Commits（zh-Hant）規範：`https://www.conventionalcommits.org/zh-hant/v1.0.0/`。

## Last Updated

- 2026-05-30: 補齊版本資訊：generate_build_info.py 加入 BUILD_TIME（打包時間）與 BUILD_DIRTY（dirty flag）；_version.py 新增 __build_time__、__dirty__；format_version_info() 加 dirty mark；GUI 版本標籤同步顯示 dirty；17 個測試全部通過。
