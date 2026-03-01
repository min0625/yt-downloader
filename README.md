# YT Downloader

本專案為以 Python 開發的 YouTube 下載工具（CLI），目標為支援影片、音訊與字幕下載流程。

> 僅供教育與學習用途，請遵守平台條款與所在地法律。

## Overview

目前本 repo 為最小可執行骨架，已完成 `pyproject.toml`、`src/` 佈局與 CLI entrypoint。

目前重點檔案如下：

- `AGENTS.md`：AI Agent 協作規範
- `MEMORY.md`：專案長期記憶
- `src/yt_downloader/__main__.py`：CLI 入口點（現階段僅最小輸出）
- `downloads/`：下載輸出目錄

## Requirements

- 作業系統：Windows（其他平台理論可行）
- Python：3.14+
- 套件管理與環境工具：`uv`

> 本專案規範統一使用 `uv`，避免直接使用 `pip` 或 `python -m pip`。

## Quick Start

```bash
uv sync --dev
uv run yt-downloader
```

## Development Commands

在本 repo 目前狀態下，可使用以下指令：

```bash
uv sync
uv sync --dev
uv run pytest
uv run ruff format
uv run ruff check
uv run ty check
uv run yt-downloader
```

## Current Status

- 目前 CLI 入口可正常執行，但功能仍屬初始狀態。
- `uv run pytest` 在現況下預期可能為 `collected 0 items`（尚未建立測試）。

## Roadmap (Suggested)

若要將本 repo 完善為可執行 CLI，建議依序完成：

1. 擴充 CLI 參數介面（URL、輸出目錄、模式與格式）
2. 建立下載 service 抽象層，避免 CLI 直接耦合底層實作
3. 新增 `tests/` 並至少覆蓋 CLI 參數解析與錯誤路徑
4. 補齊 README 的實際使用範例（影片、音訊、字幕）

## Disclaimer

本專案僅供教育與學習用途。

使用者應自行確認並遵守 YouTube 服務條款、著作權法與所在地相關法規；任何不當使用所衍生之法律責任，需由使用者自行承擔。

## License

本專案目前使用 Apache License 2.0，詳見 `LICENSE`。
