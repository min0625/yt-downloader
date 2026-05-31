# MEMORY.md

Project memory index for YT Downloader. Keep this file concise and high-signal.

## Quick Facts

- Python CLI + GUI 工具，用於下載 YouTube 影片／音訊／字幕。
- Package/environment workflow uses `uv` only；開發環境版本管理使用 `mise`（見 `mise.toml`）。
- Repo uses `src/` layout: `src/yt_downloader/`。
- `pyproject.toml`：dependencies 含 `nicegui[native]`、`yt-dlp`；dev 含 `pyinstaller`、`pytest`、`ruff`、`ty`。
- CLI 參數介面：`--url`（必要）、`--output-dir`（預設 `downloads/`）、`--mode`（`video|audio|subtitle`）、`--format`（`mp4|webm|mp3|m4a|srt|vtt`）。
- 模式偵測：`main()` 判斷 `sys.argv[1:]` 是否為空；無引數 → GUI，有引數 → CLI。
- GUI 模式以 NiceGUI 3.x 實作（`src/yt_downloader/gui.py`）：原生視窗（pywebview），port 8765，含即時進度顯示（queue + asyncio 輪詢）；Log 支援滑鼠選取、Copy Log 按鈕（clipboard API）、Export Log 按鈕（Blob 下載）。
- 下載服務：`video`、`audio`、`subtitle` 均已實作真實下載邏輯（非 stub）。
  - `video`：有 ffmpeg → 合併單檔；無 ffmpeg → 分離串流（`.video.*` + `.audio.*`）。
  - `audio`：有 ffmpeg → `FFmpegExtractAudio` 轉換；無 ffmpeg → 原生 m4a。
  - `subtitle`：優先語言 `["zh-Hant", "zh-Hans", "en"]`，有 ffmpeg 支援 srt，無 ffmpeg 退回 vtt。
- GUI Output Directory 預設為 `Path.home() / "Downloads"`（系統下載資料夾）；旁有 Browse 按鈕使用 `app.native.main_window` 開啟原生資料夾選擇對話框（`dialog_type=20` 選擇資料夾）。
- 版本格式：`format_version_compact()` 返回 `v{base}+{YYYYMMDD}.{commit}[-dirty]`，`format_version_info()` 直接回傳此格式；GUI 視窗標題與頁面底部標籤均顯示版本。
- Windows 凍結執行檔（`sys.frozen + win32`）發現無法同時保留 GUI 與 CLI 模式，因此凍結 exe 一律啟動 GUI（跳過 CLI 切換邏輯）；CLI 仰賴透過 `uv run yt-downloader` 使用。
- 測試基準：`uv run pytest` 收集 18 個測試並全部通過。
- `README.md` 為主要專案文件（zh-TW）；含免責聲明（`## Disclaimer` 章節在文件尾部）。
- 版本機制：`hatch-vcs` 從 git tag 決定版本；`_version.py` 提供 `__version__`、`__commit__`、`__ref__`、`__commit_date__`、`__build_time__`、`__dirty__`；CLI `--version` 旗標；GUI 底部顯示版本標籤（含 dirty mark）；打包前執行 `scripts/generate_build_info.py`（產出 BUILD_VERSION/BUILD_COMMIT/BUILD_BRANCH/BUILD_COMMIT_DATE/BUILD_TIME/BUILD_DIRTY）。

## Commands

- 初始環境設置：`mise install` 後執行 `mise run sync`
- Sync（安裝依賴 + 設定 git hooks）: `mise run sync`（執行 `uv sync --dev --frozen && uv run pre-commit install`）
- Release（自動觸發）: push to `main` 自動執行 `.github/workflows/release.yml`；建置 Windows exe + macOS app，並發布到 GitHub Releases （nightly pre-release）。
- Run all checks（格式化 + lint fix + ty 型別檢查 + 測試 + 打包）: `mise run check`
- Run pre-commit on all files: `uv run pre-commit run --all-files` or `mise run pre-commit`
- Run GUI: `uv run yt-downloader`（無引數）
- Run CLI: `uv run yt-downloader --url "..." --mode video --format mp4`
- Pack（含 build info 生成）: `mise run pack`
- 安裝 `ffmpeg` 後請重開終端，確認：`ffmpeg -version`、`ffprobe -version`
- Skills find: `npx skills find "<query>"`
- Skills add (project): `npx skills add <owner/repo@skill> -y`

## Architecture Notes

- CLI entrypoint is `src/yt_downloader/__main__.py`，負責模式偵測（GUI vs CLI）、參數解析與 service 分派，下載細節下放至 `src/yt_downloader/services/`。
- GUI entrypoint 是 `src/yt_downloader/gui.py`，透過 `launch()` 以 NiceGUI native 模式啟動。
- 進度顯示：GUI 透過 `queue.Queue` + progress_hook + asyncio 輪詢 (`asyncio.sleep(0.3)`) 更新 `ui.log`；`push_log()` helper 同步更新 `log_lines` list 供 Copy/Export 使用。
- Packaging script command `yt-downloader` maps to `yt_downloader.__main__:main`.
- 錯誤型別集中於 `src/yt_downloader/errors.py`（`InputError`、`DownloadError`、`DownloaderError`）。

## Pitfalls

- 文件檢查時先核對 `README.md` 與實際 repo 狀態；曾出現 `LICENSE` 已存在但文件仍寫「尚未定義授權／待補 LICENSE」的矛盾。
- 建立 PR 前先檢查 `pull_request_template.md` 與 `.github/PULL_REQUEST_TEMPLATE`；本 repo 目前沒有模板，需使用標準 PR 內文。
- 本 repo 的暫存下載輸出位於 `downloads/`，需透過 `.gitignore` 排除，避免媒體檔誤入版控。
- 進行 PR review 時先以 diff/changed files 為準，再比對 PR 內文摘要；PR 描述可能未即時反映後續 amend。
- 技能文件安全檢視需區分「教學示例」與「實際執行指令」：例如 `curl|sh`/`irm|iex` 或未參數化 SQL 可能出現在示例中，應標記為高風險樣式但不直接等同惡意。
- 若需驗證目前 CLI 介面、分派與所有服務回歸，先執行 `uv run pytest`；目前基準為 `collected 18 items` 並應全部通過。
- 若 `video` 產出為 `.video.*` + `.audio.*` 兩檔，代表目前走到無 `ffmpeg` 的 fallback 路徑；若要單檔輸出，先確認 `where ffmpeg` / `where ffprobe`。
- GUI 模式使用 NiceGUI native（pywebview）；若 pywebview 初始化失敗，請確認 `nicegui[native]` 已安裝（`uv sync --dev`）。
- 打包指令：`mise run pack`（含 `generate_build_info.py`）；輸出在 `dist/yt-downloader.exe`（Windows）或 `dist/yt-downloader` + `dist/YT Downloader.app`（macOS）。
- Windows 凍結打包陷阱：Windows exe (`console=False`) **僅支援 GUI 模式**；`main()` 在 `frozen+win32` 時直接 `launch()` GUI，不進入 CLI 分支。CLI 透過 `uv run` 使用。
- pywebview 模組名稱為 `webview`（非 `pywebview`），`webview/__pyinstaller/hook-webview.py` 提供內建 PyInstaller hook，spec 已透過 `hookspath` 引用。
- **NiceGUI Browse 按鈕 (`app.native.main_window`) 陷阱**：不可直接用 `webview.windows[0]`（NiceGUI 3.x 視窗由 NiceGUI 自行管理，`webview.windows` 為空）。正確做法：`app.native.main_window` + `getattr(window, 'create_file_dialog')(20, ...)` await 直接呼叫，`20` = `webview.FileDialog.FOLDER` 對應整數值（透過 proxy 取常數會得到 `Proxy` 型別，無法通過 ty 型別檢查）。
- **NiceGUI `WindowProxy.create_file_dialog` ty 屬性陷阱**：`WindowProxy` 透過 `__getattr__` 動態轉發，ty 無法偵測屬性。用 `getattr(window, 'create_file_dialog')(...)` 被告知回傳 `Any`，即可通過 ty。
- **pywebview dialog type 整數值**（`30 = FileDialog.SAVE`；`20 = FileDialog.FOLDER`；`10 = FileDialog.OPEN`）；舊版常數 `SAVE_DIALOG/OPEN_DIALOG/FOLDER_DIALOG` 已 deprecated，但整數值仍可直接使用。
- **NiceGUI native 匯出檔案**：在 pywebview native 模式下，browser Blob download 無法彈出系統存檔對話框；應使用 `create_file_dialog(30, save_filename=..., file_types=...)` 取得路徑，再以 Python 寫入。

## Decisions

- 文件（`README.md`、`AGENTS.md`、`MEMORY.md`、`memory/*.md`）預設使用 zh-TW；`README.md` 可保留 zh-TW。
- 程式碼（`.py`、`.toml` 等）內的所有文字（docstring、comment、error message、UI label）**統一使用英文**；`README.md` 例外。（AGENTS.md 舊版的「預設 zh-TW 程式註解」已修正為與此一致。）
- 語系調整不可改動公開介面名稱（例如 CLI 旗標、對外 API 名稱）。
- Markdown 文件的章節標題（例如 `##`、`###`）以英文為主，本文語系可依文件政策維持 zh-TW。
- Git commit 訊息採用 Conventional Commits（zh-Hant）規範：`https://www.conventionalcommits.org/zh-hant/v1.0.0/`。

## Last Updated

- 2026-05-31: fix(gui) - Export Log 加空內容防呆（`if not log_lines`）；下載 header 加入 timestamp/version/url/mode/format/output_dir；`datetime` import 加入。
- 2026-05-31: fix(gui) - Export Log 改用 native save dialog（`create_file_dialog(30, ...)`）；版本標籤加 `select-text` class 可選取複製。
- 2026-05-31: 建立 Release workflow（push to main 自動建置 nightly）；移除 SUBTASKS.md；修復 README.md 重複 Disclaimer 與錯位 bullets；AGENTS.md 更正 uv sync 指令描述。
- 2026-05-31: Windows frozen exe 改為 GUI only；版本格式改為 `v0.0.0+YYYYMMDD.commit[-dirty]`；Browse 按鈕改用 `app.native.main_window` 修復要求；GUI 視窗標題加入版本資訊。
- 2026-05-30: 修復 PR#3 review：_version.py frozen 版本讀取、spec console=True + gui.py 隱藏視窗、新增 --version 測試、MEMORY.md 符號名稱與命令修正。
- 2026-05-30: 修正文件不一致：spec console=False（非 console=True）、mise run check 含打包步驟、Pack 指令補充 mise run pack。
- 2026-05-30: 修正 MEMORY.md 過時內容：測試數量 17→18、移除不存在的 _inject_progress_hook pitfall、移除過時 pytest 路徑 pitfall、修正 Commands Pack 指令。
