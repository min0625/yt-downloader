# YT Downloader

本專案為以 Python 開發的 YouTube 下載工具，支援 **CLI** 與 **GUI** 兩種操作模式，可下載影片、音訊與字幕。

> 僅供教育與學習用途，請遵守平台條款與所在地法律。

## Overview

- **CLI 模式**：傳入參數直接執行（適合自動化或腳本）。
- **GUI 模式**：無參數啟動時，以原生視窗介面（NiceGUI + pywebview）呈現。
- 支援三種下載模式：`video`、`audio`、`subtitle`。
- 跨平台：Windows 10/11 與 macOS 11+。

主要檔案：

- `AGENTS.md`：AI Agent 協作規範
- `MEMORY.md`：專案長期記憶
- `src/yt_downloader/__main__.py`：程式入口點（模式偵測、參數解析、服務分派）
- `src/yt_downloader/gui.py`：GUI 模組（NiceGUI 3.x）
- `src/yt_downloader/services/`：下載服務層（video / audio / subtitle）
- `yt-downloader.spec`：PyInstaller 打包設定
- `downloads/`：預設下載輸出目錄

## Requirements

- Python：3.14+
- 套件管理與環境工具：[`uv`](https://docs.astral.sh/uv/)
- 開發環境版本管理：[`mise`](https://mise.jdx.dev/)
- （選用）ffmpeg + ffprobe：video 高畫質合併、audio 格式轉換、srt 字幕產出

> 本專案規範統一使用 `uv`，避免直接使用 `pip` 或 `python -m pip`。

## mise Setup

本專案使用 `mise` 管理 Node.js 與 uv 版本（見 `mise.toml`）。

```bash
# 安裝 mise（若尚未安裝）
# Windows (PowerShell): winget install jdx.mise
# macOS:                brew install mise

# 安裝 mise.toml 中指定的工具版本
mise install
```

## FFmpeg Setup

ffmpeg 為選用依賴。有安裝時可合併高畫質影片、轉換音訊格式、產出 srt 字幕；無安裝時退回分離串流或 vtt 字幕。

### Windows

```bash
winget install --id Gyan.FFmpeg -e
```

### macOS

```bash
brew install ffmpeg
```

### 確認安裝

```bash
ffmpeg -version
ffprobe -version
```

## Quick Start

```bash
# 安裝所有依賴（含 dev）
uv sync --dev

# GUI 模式（無引數，開啟原生視窗）
uv run yt-downloader

# CLI 模式（傳入參數）
uv run yt-downloader --url "https://youtu.be/..." --mode video --format mp4
```

## Development Commands

```bash
uv sync --dev              # 安裝所有依賴（含 dev）
uv run yt-downloader       # 啟動（無引數 → GUI；有引數 → CLI）
```

常用工作流可透過 `mise run` 快捷執行：

```bash
mise run sync              # 安裝依賴並設定 git hooks（初始環境設置）
mise run check             # 所有檢查：格式化、lint fix、ty 型別檢查、測試、打包
```

## Packaging

打包成單一可執行檔（需先 `uv sync --dev`，且須在目標平台執行）：

```bash
# 推薦：自動生成 build info 再打包
mise run pack

# 或手動分兩步執行
uv run python scripts/generate_build_info.py
uv run pyinstaller yt-downloader.spec
```

| 平台 | 輸出 |
|---|---|
| Windows | `dist/yt-downloader.exe` |
| macOS | `dist/yt-downloader` + `dist/YT Downloader.app` |

- **Windows**：非 console 子系統打包（`console=False`）；打包版本（.exe）**僅支援 GUI 模式**（雙擊即可使用）；CLI 模式請透過 `uv run yt-downloader` 執行。
- **macOS**：可雙擊 `.app` 開啟 GUI；或在 terminal 帶參數進入 CLI 模式。

## Current Status

- ✅ **CLI 模式**：`--url`、`--mode`、`--format`、`--output-dir` 全部實作（透過 `uv run` 使用）。
- ✅ **GUI 模式**：NiceGUI 3.x 原生視窗，含即時下載進度顯示；版本資訊顯示於視窗標題與頁面底部（格式：`v0.0.0+YYYYMMDD.commit[-dirty]`）；Browse 按鈕可開啟原生資料夾選擇對話框。
- ✅ **video**：有 ffmpeg 時合併單檔；無 ffmpeg 時輸出分離串流（`.video.*` + `.audio.*`）。
- ✅ **audio**：有 ffmpeg 時轉換 mp3/m4a；無 ffmpeg 時下載原生 m4a。
- ✅ **subtitle**：優先語言 `zh-Hant > zh-Hans > en`；有 ffmpeg 支援 srt，無 ffmpeg 退回 vtt。
- ✅ **打包**：`yt-downloader.spec` 支援 Windows / macOS。
- 測試：`uv run pytest` 目前收集 18 個測試並全部通過。

## Usage Examples

### GUI 模式

```bash
# 無引數啟動 → 開啟原生視窗介面
uv run yt-downloader
```

### CLI — Video

```bash
uv run yt-downloader \
  --url https://youtu.be/dQw4w9WgXcQ \
  --output-dir downloads/video \
  --mode video \
  --format mp4
```

### CLI — Audio

```bash
uv run yt-downloader \
  --url https://youtu.be/dQw4w9WgXcQ \
  --output-dir downloads/audio \
  --mode audio \
  --format mp3
```

### CLI — Subtitle

```bash
uv run yt-downloader \
  --url https://youtu.be/dQw4w9WgXcQ \
  --output-dir downloads/subtitle \
  --mode subtitle \
  --format srt
```

## Troubleshooting

- **缺少必要參數**：確認有提供 `--url`、`--mode`、`--format`。
- **參數值不合法**：`--mode` 須為 `video|audio|subtitle`，`--format` 須為 `mp4|webm|mp3|m4a|srt|vtt`。
- **指令無法執行**：先跑 `uv sync --dev`，再執行 `uv run yt-downloader ...`。
- **video 輸出兩個分離串流**：表示未偵測到 ffmpeg，請完成上方 FFmpeg Setup。
- **GUI 視窗未出現**：確認 `uv sync --dev` 已執行，並確認 pywebview 平台相容性。
- **打包後無法執行**：重新執行 `uv run pyinstaller yt-downloader.spec`（須在目標平台執行）。
- **播放器顯示「不支援 Opus 音效」**：使用 `--format mp4`，目前會優先選擇 `m4a` 音軌再合併輸出。
- **確認行為是否正常**：執行 `uv run pytest`，應看到測試全通過。

## Roadmap

### Completed

- CLI 參數介面（`--url`、`--output-dir`、`--mode`、`--format`）
- 下載 service 完整實作（`video`、`audio`、`subtitle` 均已接實作，非 stub）
- `tests/` 基本覆蓋（參數成功、參數錯誤、分派路徑、各 service 單元測試）
- README 使用範例與最小 Troubleshooting

### Next

- 整合測試：補充真實下載流程的端對端測試
- 版本 tag 發布流程：規劃正式 semver 標籤推送，對應 Release workflow 發布正式版本
- GUI 測試：加入基本 GUI unit test（格式切換邏輯等）

## Disclaimer

本專案僅供教育與學習用途。

使用者應自行確認並遵守 YouTube 服務條款、著作權法與所在地相關法規；任何不當使用所衍生之法律責任，需由使用者自行承擔。

## License

本專案目前使用 Apache License 2.0，詳見 `LICENSE`。
