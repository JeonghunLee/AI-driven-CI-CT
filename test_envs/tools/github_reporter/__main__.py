from __future__ import annotations

import argparse
import json
from pathlib import Path

from test_envs.tools.configuration import build_check
from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultStore

from . import post_comment, render_comment, render_environment_comment


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a normalized result to a GitHub issue")
    parser.add_argument("--latest", action="store_true", help="Use the newest result under test_envs/reports")
    parser.add_argument("--result-path", help="Use one explicit normalized result JSON")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--message", help="Post a workflow error when no normalized result exists")
    parser.add_argument("--environment-check", action="store_true", help="Detect this runner and post its environment")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.environment_check:
        comment = render_environment_comment(build_check())
        if args.dry_run:
            print(comment)
        else:
            post_comment(args.issue, comment)
        return
    if args.message:
        comment = f"## Test Result\n\n**Result: ERROR**\n\n{args.message}"
        if args.dry_run:
            print(comment)
        else:
            post_comment(args.issue, comment)
        return
    store = ResultStore()
    result_path = Path(args.result_path) if args.result_path else store.latest()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    result = store.load(result_path)
    analysis_payload = payload.get("test_analysis", {}).get("analysis")
    if isinstance(analysis_payload, dict):
        analysis = Analysis(**analysis_payload)
    elif result.category.lower() == "unit":
        analysis = Analysis(
            summary="Local LLM analysis is not used for unittest results.",
            classification="unittest",
            confidence=1.0,
            source="not-used",
            recommendations="Review failed function details and the result log.",
        )
    else:
        analysis = Analysis(
            summary="Local LLM analysis was not generated. Review the workflow run and test log.",
            classification="report-error",
            confidence=0.0,
            source="not-available",
            recommendations="Review the report-generation failure and rerun the request.",
            needs_escalation=True,
        )
    comment = render_comment(result, analysis)
    if args.dry_run:
        print(comment)
    else:
        post_comment(args.issue, comment)


if __name__ == "__main__":
    main()
