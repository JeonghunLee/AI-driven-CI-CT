from __future__ import annotations

import argparse
import json

from . import generate_latest_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown from the most recent test result")
    parser.add_argument("--docs", action="store_true", help="Also copy the report into docs/test")
    parser.add_argument("--source-review", action="store_true")
    parser.add_argument("--model", help="Override test_envs/configs/config.json for this report")
    args = parser.parse_args()
    output = generate_latest_markdown(args.docs, args.source_review, args.model)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
