from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path

from yt_downloader.errors import DownloadError, InputError
from yt_downloader.services import DownloadRequest, get_service

MODES = ("video", "audio", "subtitle")
FORMATS = ("mp4", "webm", "mp3", "m4a", "srt", "vtt")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="yt-downloader")
    parser.add_argument("--url", required=True, help="YouTube URL")
    parser.add_argument(
        "--output-dir",
        default="downloads/",
        help="Output directory for downloads (default: downloads/)",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=MODES,
        help="Download mode: video / audio / subtitle",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=FORMATS,
        help="Output format (restricted to allowed values)",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    return build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    # When argv is None, read actual command-line args; with args enter CLI mode, without args launch GUI
    effective_args = list(argv) if argv is not None else sys.argv[1:]

    if not effective_args:
        from yt_downloader.gui import launch  # noqa: PLC0415

        launch()
        return 0

    args = parse_args(argv)
    request = DownloadRequest(
        url=args.url,
        output_dir=Path(args.output_dir),
        format=args.format,
    )

    try:
        service = get_service(args.mode)
        service.download(request)
    except (InputError, DownloadError) as exc:
        print(f"Error: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
