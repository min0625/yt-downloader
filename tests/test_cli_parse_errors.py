import pytest

from yt_downloader.__main__ import parse_args


def test_parse_args_missing_required_url(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        parse_args(["--mode", "video", "--format", "mp4"])

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert "the following arguments are required: --url" in captured.err


def test_parse_args_invalid_format(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        parse_args(
            [
                "--url",
                "https://youtu.be/dQw4w9WgXcQ",
                "--mode",
                "video",
                "--format",
                "invalid",
            ]
        )

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert "argument --format: invalid choice" in captured.err
