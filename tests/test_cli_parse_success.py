from yt_downloader.__main__ import parse_args


def test_parse_args_success() -> None:
    args = parse_args(
        [
            "--url",
            "https://youtu.be/dQw4w9WgXcQ",
            "--output-dir",
            "downloads/custom",
            "--mode",
            "video",
            "--format",
            "mp4",
        ]
    )

    assert args.url == "https://youtu.be/dQw4w9WgXcQ"
    assert args.output_dir == "downloads/custom"
    assert args.mode == "video"
    assert args.format == "mp4"
