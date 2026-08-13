from __future__ import annotations

import argparse
import json

from tools.local_llm import Analysis
from tools.result_normalizer import ResultStore

from . import post_comment, render_comment


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a normalized result to a GitHub issue")
    parser.add_argument("--latest", action="store_true", help="Use the newest result under reports/logs")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    store = ResultStore()
    result = store.load()
    analysis = Analysis(**json.loads((store.latest().parent / "analysis.json").read_text(encoding="utf-8")))
    comment = render_comment(result, analysis)
    if args.dry_run:
        print(comment)
    else:
        post_comment(args.issue, comment)


if __name__ == "__main__":
    main()
