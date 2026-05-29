# SUBTASKS

此檔案將 `README.md` 的 Roadmap 拆分為可執行子任務，便於逐步追蹤。

## 1) CLI 參數介面

- [x] 新增 `--url`（必要）參數。
- [x] 新增 `--output-dir`（預設 `downloads/`）參數。
- [x] 新增 `--mode`（`video` / `audio` / `subtitle`）參數。
- [x] 新增 `--format` 參數並限制可接受值。
- [x] 補上參數缺失與非法值的錯誤訊息。

## 2) 下載服務抽象層

- [x] 建立 `services/` 模組，定義下載介面。
- [x] 建立對應模式的 service stub（video/audio/subtitle）。
- [x] 讓 CLI 只負責參數解析與分派，不直接處理下載細節。
- [x] 將錯誤型別集中化（例如輸入錯誤、下載失敗）。

## 3) 測試覆蓋

- [x] 建立 `tests/` 目錄與基本測試結構。
- [x] 測試 CLI 參數解析（成功路徑）。
- [x] 測試參數錯誤路徑（缺參數、非法值）。
- [x] 測試服務層呼叫分派是否正確。

## 4) README 使用範例

- [x] 增加影片下載指令範例。
- [x] 增加音訊下載指令範例。
- [x] 增加字幕下載指令範例。
- [x] 補充常見錯誤與排查建議（最小版本）。

## 5) GUI 模式

- [x] 新增 NiceGUI 依賴（`nicegui[native]`）。
- [x] 建立 `src/yt_downloader/gui.py`：URL 輸入、模式選擇、格式選擇、輸出目錄、下載按鈕、即時進度 log。
- [x] 更新 `__main__.py` 加入模式偵測（無引數 → GUI；有引數 → CLI）。
- [x] Windows：GUI 啟動時呼叫 `ShowWindow` 隱藏 console 視窗。

## 6) 完整服務實作

- [x] `audio` 服務：有 ffmpeg → `FFmpegExtractAudio` 轉換；無 ffmpeg → 原生 m4a。
- [x] `subtitle` 服務：有 ffmpeg → 支援 srt；無 ffmpeg → 自動退回 vtt。
- [x] 補齊 audio / subtitle 服務測試（各 4 個）。

## 7) 打包為可執行檔

- [x] 新增 `pyinstaller` 至 dev 依賴。
- [x] 建立 `yt-downloader.spec`：收集 NiceGUI / pywebview 靜態資源，支援 Windows（onefile console）與 macOS（.app bundle）。

## 建議執行順序

1. 先完成 CLI 參數介面（Task 1）。
2. 再完成服務抽象層（Task 2）。
3. 同步補上測試（Task 3）。
4. 最後更新文件範例（Task 4）。
