from __future__ import annotations

import argparse
import json

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultStore

from . import post_comment, render_comment


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a normalized result to a GitHub issue")
    parser.add_argument("--latest", action="store_true", help="Use the newest result under test_envs/reports")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    store = ResultStore()
    result_path = store.latest()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    result = store.load(result_path)
    analysis = Analysis(**payload["test_analysis"]["analysis"])
    comment = render_comment(result, analysis)
    if args.dry_run:
        print(comment)
    else:
        post_comment(args.issue, comment)


if __name__ == "__main__":
    main()
