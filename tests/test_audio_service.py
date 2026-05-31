import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from yt_downloader.errors import DownloadError, InputError
from yt_downloader.services.audio import AudioDownloadService
from yt_downloader.services.base import DownloadRequest


class FakeYoutubeDL:
    def __init__(self, options: dict, result_code: int) -> None:
        self.options = options
        self.result_code = result_code
        self.download_urls: list[str] | None = None

    def __enter__(self) -> FakeYoutubeDL:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    def download(self, urls: list[str]) -> int:
        self.download_urls = urls
        return self.result_code


def test_audio_download_mp3_with_ffmpeg(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    created_instances: list[FakeYoutubeDL] = []

    def fake_youtube_dl(options: dict) -> FakeYoutubeDL:
        instance = FakeYoutubeDL(options, result_code=0)
        created_instances.append(instance)
        return instance

    monkeypatch.setattr(
        "yt_downloader.services.base.shutil.which", lambda _: "/usr/bin/tool"
    )
    monkeypatch.setitem(
        sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=fake_youtube_dl)
    )

    service = AudioDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path / "audio",
        format="mp3",
    )
    service.download(request)

    assert len(created_instances) == 1
    opts = created_instances[0].options
    assert opts["format"] == "bestaudio/best"
    assert "postprocessors" in opts
    assert opts["postprocessors"][0]["preferredcodec"] == "mp3"
    assert created_instances[0].download_urls == ["https://youtu.be/dQw4w9WgXcQ"]


def test_audio_download_m4a_without_ffmpeg(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    created_instances: list[FakeYoutubeDL] = []

    def fake_youtube_dl(options: dict) -> FakeYoutubeDL:
        instance = FakeYoutubeDL(options, result_code=0)
        created_instances.append(instance)
        return instance

    # neither system ffmpeg nor bundled ffmpeg present
    monkeypatch.setattr("yt_downloader.services.base.shutil.which", lambda _: None)
    monkeypatch.setattr(
        "yt_downloader.services.base._get_bundled_ffmpeg_exe", lambda: None
    )
    monkeypatch.setitem(
        sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=fake_youtube_dl)
    )

    service = AudioDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path / "audio",
        format="m4a",
    )
    service.download(request)

    assert len(created_instances) == 1
    opts = created_instances[0].options
    assert "m4a" in opts["format"]
    assert "postprocessors" not in opts


def test_audio_download_invalid_format(tmp_path: Path) -> None:
    service = AudioDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path / "audio",
        format="mp4",
    )
    with pytest.raises(InputError, match="audio mode does not support format"):
        service.download(request)


def test_audio_download_nonzero_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_youtube_dl(options: dict) -> FakeYoutubeDL:
        return FakeYoutubeDL(options, result_code=1)

    monkeypatch.setattr(
        "yt_downloader.services.base.shutil.which", lambda _: "/usr/bin/tool"
    )
    monkeypatch.setitem(
        sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=fake_youtube_dl)
    )

    service = AudioDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path / "audio",
        format="mp3",
    )
    with pytest.raises(DownloadError, match="Audio download failed"):
        service.download(request)
