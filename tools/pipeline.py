from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from tools.codex_escalation import evaluate
from tools.deepseek import DeepSeekAnalyzer
from tools.log_parser import parse_files
from tools.mkdocs_reporter import MarkdownReporter
from tools.result_normalizer import ResultStore


def run(publish_docs: bool = False, review_source: bool = False) -> dict[str, object]:
    store = ResultStore()
    result_path = store.latest()
    result = store.load(result_path)
    execution_dir = result_path.parent
    logs = parse_files([execution_dir / filename for filename in result.logs.values()])
    source_diff = _source_diff() if review_source else ""
    analysis = DeepSeekAnalyzer().analyze(result, logs, source_diff)
    decision = evaluate(result, analysis, repeated_failures=_consecutive_failures(store, result.test_id))

    analysis_path = execution_dir / "analysis.json"
    analysis_path.write_text(json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    escalation_path = execution_dir / "codex-escalation.json"
    escalation_path.write_text(
        json.dumps({"required": decision.required, "reasons": decision.reasons}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown = MarkdownReporter(reports_root=store.root).generate(
        result, analysis, logs.important, publish_docs=publish_docs
    )
    return {
        "result_data": str(result_path),
        "markdown": str(markdown),
        "analysis": str(analysis_path),
        "published_to_mkdocs": publish_docs,
        "codex_escalation": decision.required,
        "escalation_reasons": decision.reasons,
    }


def _source_diff() -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--unified=3"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _consecutive_failures(store: ResultStore, test_id: str) -> int:
    records = []
    for path in (store.root / "logs" / test_id).glob("*/result.json"):
        try:
            records.append(store.load(path))
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
    count = 0
    for item in sorted(records, key=lambda value: value.timestamp, reverse=True):
        if item.status not in {"FAIL", "ERROR"}:
            break
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze the latest test and create a Markdown-first report")
    parser.add_argument("--latest", action="store_true", help="Compatibility flag; latest is always processed")
    parser.add_argument("--docs", action="store_true", help="Also publish the canonical Markdown into docs/test")
    parser.add_argument("--source-review", action="store_true", help="Include the local git diff in DeepSeek analysis")
    args = parser.parse_args()
    print(json.dumps(run(publish_docs=args.docs, review_source=args.source_review), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
