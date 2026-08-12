from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.ollama import Analysis
from tools.result_normalizer import ResultRecord, ResultStore


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _items(values: dict[str, Any]) -> str:
    return "\n".join(f"- **{_cell(key)}:** {_cell(value)}" for key, value in values.items()) or "- None"


class MkDocsReporter:
    def __init__(self, docs_root: str | Path = "docs", reports_root: str | Path = "reports") -> None:
        self.docs_root = Path(docs_root)
        self.store = ResultStore(reports_root)

    def generate(self, result: ResultRecord, analysis: Analysis, important_logs: list[str] | None = None) -> Path:
        category = result.category.lower().replace(" ", "-")
        if category == "unit":
            destination = self.docs_root / "test" / "unit" / f"{result.test_id}.md"
        else:
            destination = self.docs_root / "test" / "ct" / category / f"{result.test_id}.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        history = self._history(result.test_id)
        history_rows = "\n".join(
            "| " + " | ".join(
                _cell(value) for value in (
                    item.timestamp, item.execution_id, item.commit, item.status,
                    f"{item.duration:.3f}", item.statistics.get("mean", "-"), item.runner,
                )
            ) + " |"
            for item in history
        ) or "| - | - | - | - | - | - | - |"
        logs = "\n".join(f"- `{_cell(line)}`" for line in (important_logs or [])) or "- No error or warning extracted."
        issue = result.metrics.get("issue_url", "Not associated")
        body = f"""# {result.test_id}

## Latest result

- **Status:** {result.status}
- **Category:** {result.category}
- **Execution ID:** {result.execution_id}
- **Duration:** {result.duration:.3f} seconds
- **Interface:** {result.interface}
- **Equipment:** {result.equipment}
- **Commit:** `{result.commit}`
- **Runner:** {result.runner}
- **GitHub Issue:** {issue}

## Measurements

{_items(dict(result.metrics))}

## Statistics

{_items(dict(result.statistics))}

## Important log

{logs}

## AI analysis

{analysis.summary}

- Classification: `{analysis.classification}`
- Confidence: {analysis.confidence:.2f}
- Source: `{analysis.source}`

## Test history

| Date | Execution ID | Commit | Status | Duration (s) | Mean | Runner |
|---|---|---|---|---:|---:|---|
{history_rows}
"""
        destination.write_text(body, encoding="utf-8")
        return destination

    def _history(self, test_id: str) -> list[ResultRecord]:
        items: list[ResultRecord] = []
        for path in sorted((self.store.root / "json").glob(f"{test_id}-*.json")):
            try:
                items.append(self.store.load(path))
            except (ValueError, TypeError, json.JSONDecodeError):
                continue
        return sorted(items, key=lambda item: item.timestamp, reverse=True)


__all__ = ["MkDocsReporter"]
