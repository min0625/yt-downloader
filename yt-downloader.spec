# yt-downloader.spec
#
# 用法：
#   Windows:  uv run pyinstaller yt-downloader.spec
#   macOS:    uv run pyinstaller yt-downloader.spec
#
# 輸出：
#   Windows:  dist/yt-downloader.exe  （console 模式；GUI 模式會自動隱藏 console 視窗）
#   macOS:    dist/yt-downloader      （executable）
#             dist/YT Downloader.app  （.app bundle，可直接雙擊）
#
# 打包前請先確認依賴已安裝：uv sync --dev

import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ---------- NiceGUI 靜態資源（CSS / JS / HTML templates） ----------
nicegui_datas = collect_data_files("nicegui")

# ---------- NiceGUI 動態 import 的子模組 ----------
nicegui_hiddenimports = collect_submodules("nicegui")

# ---------- pywebview（模組名稱為 webview）----------
import webview as _webview

_webview_hooks = os.path.join(os.path.dirname(_webview.__file__), "__pyinstaller")
webview_datas = collect_data_files("webview")
webview_hiddenimports = collect_submodules("webview")

# ---------- Analysis ----------
a = Analysis(
    ["src/yt_downloader/__main__.py"],
    pathex=["."],
    binaries=[],
    datas=nicegui_datas + webview_datas,
    hiddenimports=nicegui_hiddenimports
    + webview_hiddenimports
    + [
        "yt_dlp",
        "yt_downloader.gui",
        "yt_downloader.services.video",
        "yt_downloader.services.audio",
        "yt_downloader.services.subtitle",
    ],
    # 使用 pywebview 內建 hook（收集 Windows DLL 與 JS 資源）
    hookspath=[_webview_hooks],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="yt-downloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=True：保留 console 以支援 CLI 模式；
    # GUI 模式下 gui.py 會在 Windows 上呼叫 ShowWindow(hwnd, 0) 隱藏視窗
    console=True,
    onefile=True,
)

# macOS：另外輸出 .app bundle（可雙擊開啟）
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="YT Downloader.app",
        icon=None,
        bundle_identifier="com.yt-downloader",
        info_plist={
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
        },
    )
