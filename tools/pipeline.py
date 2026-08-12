from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from tools.codex_escalation import evaluate
from tools.log_parser import parse_files
from tools.mkdocs_reporter import MkDocsReporter
from tools.ollama import OllamaAnalyzer
from tools.result_normalizer import ResultStore


def run(generate_docs: bool = True) -> dict[str, object]:
    store = ResultStore()
    result = store.load()
    execution_dir = store.root / "logs" / result.test_id / result.execution_id
    logs = parse_files([execution_dir / filename for filename in result.logs.values()])
    analysis = OllamaAnalyzer().analyze(result, logs)
    decision = evaluate(result, analysis, repeated_failures=_consecutive_failures(store, result.test_id))

    analysis_path = execution_dir / "analysis.json"
    analysis_path.write_text(json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    shutil.copyfile(analysis_path, store.root / "json" / "latest-analysis.json")
    escalation_path = execution_dir / "codex-escalation.json"
    escalation_path.write_text(
        json.dumps({"required": decision.required, "reasons": decision.reasons}, indent=2), encoding="utf-8"
    )

    doc_path: Path | None = None
    if generate_docs:
        doc_path = MkDocsReporter(reports_root=store.root).generate(result, analysis, logs.important)
    return {
        "result": str(store.latest()),
        "analysis": str(analysis_path),
        "report": str(doc_path) if doc_path else None,
        "codex_escalation": decision.required,
        "escalation_reasons": decision.reasons,
    }


def _consecutive_failures(store: ResultStore, test_id: str) -> int:
    records = []
    for path in (store.root / "json").glob(f"{test_id}-*.json"):
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
    parser = argparse.ArgumentParser(description="Analyze the latest CI/CT result and generate outputs")
    parser.add_argument("--latest", action="store_true", help="Process reports/json/latest.json")
    parser.add_argument("--docs", action="store_true", help="Generate the MkDocs test report")
    args = parser.parse_args()
    print(json.dumps(run(generate_docs=args.docs), indent=2))


if __name__ == "__main__":
    main()

