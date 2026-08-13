from __future__ import annotations

import argparse

from . import FORMATS, convert, latest_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a test Markdown report with Pandoc")
    parser.add_argument("source", nargs="?")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--format", choices=FORMATS, default="html")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    source = latest_markdown() if args.latest else args.source
    if not source:
        parser.error("source or --latest is required")
    print(convert(source, args.format, args.output_dir))


if __name__ == "__main__":
    main()
