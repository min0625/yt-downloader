from yt_downloader.__main__ import main
from yt_downloader.services.base import DownloadRequest


class DummyService:
    def __init__(self) -> None:
        self.called_request: DownloadRequest | None = None

    def download(self, request: DownloadRequest) -> None:
        self.called_request = request


def test_main_dispatches_to_service(monkeypatch) -> None:
    dummy_service = DummyService()
    called_mode: list[str] = []

    def fake_get_service(mode: str) -> DummyService:
        called_mode.append(mode)
        return dummy_service

    monkeypatch.setattr("yt_downloader.__main__.get_service", fake_get_service)

    exit_code = main(
        [
            "--url",
            "https://youtu.be/dQw4w9WgXcQ",
            "--output-dir",
            "downloads/testing",
            "--mode",
            "audio",
            "--format",
            "mp3",
        ]
    )

    assert exit_code == 0
    assert called_mode == ["audio"]
    assert dummy_service.called_request is not None
    assert dummy_service.called_request.url == "https://youtu.be/dQw4w9WgXcQ"
    assert dummy_service.called_request.output_dir.as_posix() == "downloads/testing"
    assert dummy_service.called_request.format == "mp3"
