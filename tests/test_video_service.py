import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from yt_downloader.errors import DownloadError, InputError
from yt_downloader.services.base import DownloadRequest
from yt_downloader.services.video import VideoDownloadService


class FakeYoutubeDL:
    def __init__(self, options: dict[str, object], result_code: int) -> None:
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


def test_video_download_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    created_instances: list[FakeYoutubeDL] = []

    def fake_youtube_dl(options: dict[str, object]) -> FakeYoutubeDL:
        instance = FakeYoutubeDL(options, result_code=0)
        created_instances.append(instance)
        return instance

    monkeypatch.setattr(
        "yt_downloader.services.base.shutil.which", lambda _: "C:/ffmpeg/bin/tool"
    )
    monkeypatch.setitem(
        sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=fake_youtube_dl)
    )

    service = VideoDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path / "video",
        format="mp4",
    )

    service.download(request)

    assert request.output_dir.exists()
    assert len(created_instances) == 1

    instance = created_instances[0]
    assert instance.download_urls == ["https://youtu.be/dQw4w9WgXcQ"]
    assert (
        instance.options["format"]
        == "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    )
    assert instance.options["merge_output_format"] == "mp4"
    assert str(instance.options["outtmpl"]).endswith("%(title)s.%(ext)s")


def test_video_download_invalid_format(tmp_path: Path) -> None:
    service = VideoDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path,
        format="mp3",
    )

    with pytest.raises(InputError):
        service.download(request)


def test_video_download_nonzero_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    created_instances: list[FakeYoutubeDL] = []

    def fake_youtube_dl(options: dict[str, object]) -> FakeYoutubeDL:
        instance = FakeYoutubeDL(options, result_code=1)
        created_instances.append(instance)
        return instance

    monkeypatch.setattr(
        "yt_downloader.services.base.shutil.which", lambda _: "C:/ffmpeg/bin/tool"
    )
    monkeypatch.setitem(
        sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=fake_youtube_dl)
    )

    service = VideoDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path,
        format="webm",
    )

    with pytest.raises(DownloadError):
        service.download(request)

    assert len(created_instances) == 1


def test_video_download_fallback_without_ffmpeg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    created_instances: list[FakeYoutubeDL] = []

    def fake_youtube_dl(options: dict[str, object]) -> FakeYoutubeDL:
        instance = FakeYoutubeDL(options, result_code=0)
        created_instances.append(instance)
        return instance

    monkeypatch.setattr("yt_downloader.services.base.shutil.which", lambda _: None)
    monkeypatch.setitem(
        sys.modules, "yt_dlp", SimpleNamespace(YoutubeDL=fake_youtube_dl)
    )

    service = VideoDownloadService()
    request = DownloadRequest(
        url="https://youtu.be/dQw4w9WgXcQ",
        output_dir=tmp_path,
        format="mp4",
    )

    service.download(request)

    assert len(created_instances) == 2
    video_instance = created_instances[0]
    audio_instance = created_instances[1]
    assert (
        video_instance.options["format"]
        == "bestvideo[ext=mp4]/bestvideo/best[ext=mp4]/best"
    )
    assert (
        audio_instance.options["format"]
        == "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio"
    )
    assert str(video_instance.options["outtmpl"]).endswith("%(title)s.video.%(ext)s")
    assert str(audio_instance.options["outtmpl"]).endswith("%(title)s.audio.%(ext)s")
