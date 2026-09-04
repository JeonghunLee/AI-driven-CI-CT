from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from test_envs.tools.codex_escalation import EscalationDecision, evaluate
from test_envs.tools.local_llm import Analysis, LocalLLMAnalyzer
from test_envs.tools.log_parser import parse_files
from test_envs.tools.mkdocs_reporter import MarkdownReporter
from test_envs.tools.result_normalizer import ResultStore


def run(
    publish_docs: bool = False,
    review_source: bool = False,
    model: str | None = None,
    result_path: str | Path | None = None,
) -> dict[str, object]:
    store = ResultStore()
    result_path = Path(result_path) if result_path else store.latest()
    result = store.load(result_path)
    report_dir = result_path.parent
    logs = parse_files([report_dir / filename for filename in result.logs.values()])
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    if result.category.lower() == "unit":
        analysis = Analysis("", "unittest", 1.0, "not-used")
        decision = EscalationDecision(False, ())
        local_llm_model = "not-used"
        payload.pop("test_analysis", None)
    else:
        source_diff = _source_diff() if review_source else ""
        analyzer = LocalLLMAnalyzer(model=model)
        analysis = analyzer.analyze(result, logs, source_diff)
        decision = evaluate(result, analysis, repeated_failures=_consecutive_failures(store, result.test_id))
        local_llm_model = analyzer.model
        payload["test_analysis"] = {
            "analysis": analysis.to_dict(),
            "escalation": {"required": decision.required, "reasons": decision.reasons},
        }
    result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown = MarkdownReporter(reports_root=store.root).generate(
        result, analysis, logs.important, publish_docs=publish_docs
    )
    return {
        "result_data": str(result_path),
        "markdown": str(markdown),
        "analysis": str(result_path),
        "local_llm_model": local_llm_model,
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
    for path in store.result_paths(test_id):
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
    parser.add_argument("--result-path", help="Process one explicit normalized result JSON")
    parser.add_argument("--docs", action="store_true", help="Also publish the canonical Markdown into docs/tests")
    parser.add_argument("--source-review", action="store_true", help="Include the local git diff in Local LLM analysis")
    parser.add_argument("--model", help="Override test_envs/configs/config.json for this analysis")
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                publish_docs=args.docs,
                review_source=args.source_review,
                model=args.model,
                result_path=args.result_path,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
