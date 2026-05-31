# AGENTS.md

此文件定義本專案（YT Downloader）的 AI Agent 協作規範。

## Project Overview

- 本專案為 Python 工具，支援 **CLI**（命令列）與 **GUI**（原生視窗）兩種模式，用於下載 YouTube 影片／音訊／字幕。
- 套件管理與環境工具統一使用 [`uv`](https://docs.astral.sh/uv/)。
- 開發環境版本管理使用 [`mise`](https://mise.jdx.dev/)（見 `mise.toml`）。
- 變更以「小範圍、精準修改」為原則；除非明確要求，避免大型重構。

## Instruction Priority

若規範衝突，依以下順序判定：

1. 使用者在對話中的直接需求
2. 距離目標檔案最近的 `AGENTS.md`
3. 專案根目錄（或上層）`AGENTS.md`
4. 其他文件（例如 `README.md`、程式內註解）

## Document and Comment Language

- 文件（如 `README.md`、`AGENTS.md`、`MEMORY.md`、`memory/*.md`）預設使用 zh-TW。
- 程式碼（`.py`、`.toml` 等）內的所有文字（docstring、comment、error message、UI label）**統一使用英文**；`README.md` 例外。
- 對外 API、CLI 旗標與既有公開介面名稱不得僅因語系調整而變更。
- 進行翻譯或語氣調整時，需保持技術語意與可執行指令不變。

## Development Environment and Installation

- 禁止直接使用 `pip` 或 `python -m pip`。
- 初始環境設置：`mise install` 後再執行 `mise run sync`
- 安裝開發相依：`mise run sync`（執行 `uv sync --dev --frozen` 並設定 git hooks）
- 執行專案命令時使用：`uv run <cmd>` 或 `mise run <task>`

## Common Commands

- Sync（安裝依賴 + 設定 git hooks）: `mise run sync`
- Check（全部：格式化 + lint fix + ty 型別檢查 + 測試 + 打包）: `mise run check`
- Run GUI: `uv run yt-downloader`（無引數）
- Run CLI: `uv run yt-downloader --url "..." --mode video --format mp4`
- Pack（含 build info 生成）: `mise run pack`

## Code Style and Quality

- 保持與 Python 3.14+ 相容。
- 遵循 `pyproject.toml` 既有設定。
- 優先使用清晰命名與小型函式，避免過度抽象。
- 除非任務必要，避免新增相依套件。

## Change Policy

- 優先修正根因，而非表面補丁。
- 變更範圍需緊扣使用者需求。
- 不可在未說明下改動公開行為或 CLI 旗標。
- 當行為或命令改變時，必須同步更新相關文件。
- 不要為了風格偏好而改動不相關檔案。

## Git Commit Message Style

- Git commit 訊息採用 Conventional Commits（zh-Hant）：https://www.conventionalcommits.org/zh-hant/v1.0.0/
- 基本格式：`<type>[optional scope]: <description>`
- 重大變更需使用 `!` 或在 footer 加上 `BREAKING CHANGE:`。
- `type` 建議使用：`feat`、`fix`、`docs`、`refactor`、`test`、`chore`、`build`、`ci`、`perf`、`revert`。
- `description` 使用祈使句、精簡描述單一變更，避免模糊訊息（例如 `update`、`misc`）。
- 範例：`feat(cli): add subtitle language option`
- 範例：`fix(download): handle age-restricted video metadata`

## Validation Checklist (Before Completion)

- 先跑與變更最相關的檢查，再視情況擴大。
- 若失敗屬既有且與本次變更無關，需明確回報，不過度修補。
- 確保文件中調整過的命令與路徑可在本 repo 執行。

## Skills Usage Guidelines

Skill 文件位於 `.agents/skills/*/SKILL.md`。

- 遇到特定領域任務時，優先讀取對應 skill（例如 `uv-package-manager`、`python-pro`、`python-configuration`）。
- 進行該領域的實作前，先吸收對應 skill 指引。

## Agent Memory Mechanism (`MEMORY.md`)

`MEMORY.md` 為跨回合共享的長期專案記憶。

以下規範對本 repo 的 AI Agent 為強制要求。

### Required Workflow

- 任務開始：進行主要實作前先讀取 `MEMORY.md`。
- 任務進行中：若發現可重用知識，先整理成精簡筆記。
- 任務結束前：更新 `MEMORY.md`（必要時含 `memory/*.md`）再交付。
- 若沒有可長期重用資訊，避免寫入噪音內容。

### What to Preserve

- 穩定命令、環境注意事項、架構事實、可重現的除錯模式。
- 可跨 session 重用的決策與團隊慣例。
- 僅保存 repo 範圍資訊，不保存一次性任務對話。

### What Not to Preserve

- 機密、Token、個資、或機器專屬私有路徑。
- 暫時性錯誤、短期日誌、未驗證推測。
- 已在 `AGENTS.md`／`README.md` 充分描述且無額外價值的重複內容。

### Purpose

- 保存跨 session 的穩定專案知識。
- 降低重複探索命令、架構與常見陷阱的成本。
- 將長期可重用資訊放在記憶，而非任務流水帳。

### Location

- 主索引：repo 根目錄 `MEMORY.md`
- 細節頁：`memory/*.md`（視需要建立）

### Maintenance Rules

- 若 `MEMORY.md` 不存在，請依本文件建議章節建立。
- `MEMORY.md` 應維持索引型摘要；詳細內容移至 `memory/*.md`。
- 高訊號內容放前面，前 200 行優先保留核心資訊。
- 只更新可重用、repo 範圍內的知識。
- 內容保持精簡、可執行、可驗證。
- 發現過時資訊時，應替換或刪除，不採無限追加。
- 絕不寫入機密、Token、個資、或機器私有路徑。
- 每次編輯記憶時，需同步更新 `## Last Updated`（日期＋原因）。

### Suggested Sections

- `## Quick Facts`
- `## Commands`
- `## Architecture Notes`
- `## Pitfalls`
- `## Decisions`
- `## Last Updated`

### Entry Quality Standards

- 使用祈使句與可驗證敘述（命令、路徑、條件）。
- 優先採「當 X 時，做 Y」格式。
- 若摘要過長，改連結到 `memory/*.md` 細節頁（如 `memory/debugging.md`）。
