from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.deepseek import Analysis
from tools.result_normalizer import ResultRecord, ResultStore


def _safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _items(values: dict[str, Any]) -> str:
    return "\n".join(f"- **{_safe(key)}:** {_safe(value)}" for key, value in values.items()) or "- None"


class MarkdownReporter:
    """Create the canonical human-readable report and optionally publish it to MkDocs."""

    def __init__(self, reports_root: str | Path = "reports", docs_root: str | Path = "docs") -> None:
        self.store = ResultStore(reports_root)
        self.docs_root = Path(docs_root)

    def generate(
        self,
        result: ResultRecord,
        analysis: Analysis,
        important_logs: list[str] | None = None,
        publish_docs: bool = False,
    ) -> Path:
        destination = self.store.root / "markdown" / result.test_id / result.execution_id / "result.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.render(result, analysis, important_logs), encoding="utf-8")

        latest = self.store.root / "markdown" / result.test_id / "latest.md"
        latest.write_text(destination.read_text(encoding="utf-8"), encoding="utf-8")
        if publish_docs:
            self.publish(destination, result)
        return destination

    def publish(self, source: Path, result: ResultRecord) -> Path:
        if result.category.lower() == "unit":
            latest_target = self.docs_root / "test" / "unit" / f"{result.test_id}.md"
        else:
            category = result.category.lower().replace(" ", "-")
            latest_target = self.docs_root / "test" / "ct" / category / f"{result.test_id}.md"
        execution_dir = latest_target.with_suffix("")
        execution_dir.mkdir(parents=True, exist_ok=True)

        canonical_dir = self.store.root / "markdown" / result.test_id
        for canonical in canonical_dir.glob("*/result.md"):
            execution_id = canonical.parent.name
            (execution_dir / f"{execution_id}.md").write_text(
                canonical.read_text(encoding="utf-8"), encoding="utf-8"
            )

        snapshots = sorted(execution_dir.glob("*.md"), key=lambda path: path.stem, reverse=True)
        links = "\n".join(f"- [{path.stem}]({result.test_id}/{path.name})" for path in snapshots)
        latest_content = source.read_text(encoding="utf-8")
        latest_target.write_text(
            f"{latest_content}\n## Execution documents\n\n{links or '- None'}\n",
            encoding="utf-8",
        )
        return execution_dir / f"{result.execution_id}.md"

    def render(self, result: ResultRecord, analysis: Analysis, important_logs: list[str] | None = None) -> str:
        history = self._history(result.test_id)
        history_rows = "\n".join(
            f"| {_safe(item.timestamp)} | {_safe(item.execution_id)} | {_safe(item.commit)} | "
            f"{item.status} | {item.duration:.3f} | {_safe(item.environment)} |"
            for item in history
        ) or "| - | - | - | - | - | - |"
        logs = "\n".join(f"- `{_safe(line)}`" for line in (important_logs or [])) or "- None"
        warnings = "\n".join(
            f"- **{_safe(item.get('severity', 'Important'))}:** {_safe(item.get('message', ''))}"
            for item in analysis.warnings
        ) or "- None"
        return f"""# {result.test_id} Test Result

## Test summary

- **Description:** {_safe(result.description)}
- **Environment:** {_safe(result.environment)}
- **Configuration:** {_safe(dict(result.configuration))}
- **Equipment:** {_safe(result.equipment)}
- **Interface:** {_safe(result.interface)}
- **Result:** **{result.status}**
- **Execution time:** {result.duration:.3f} seconds
- **Execution date:** {_safe(result.timestamp)}
- **Commit / revision:** `{_safe(result.commit)}`
- **Execution ID:** `{_safe(result.execution_id)}`

## Measurement

{_items(dict(result.metrics))}

## Statistics

{_items(dict(result.statistics))}

## Important logs

{logs}

## Warnings

{warnings}

## DeepSeek analysis

{analysis.summary}

- **Classification:** `{_safe(analysis.classification)}`
- **Confidence:** {analysis.confidence:.2f}
- **Analyzer:** `{_safe(analysis.source)}`

### Failure analysis

{analysis.failure_analysis or "Not applicable"}

### Source review

{analysis.source_review}

## Test history

| Date | Execution ID | Commit | Result | Duration (s) | Environment |
|---|---|---|---|---:|---|
{history_rows}
"""

    def _history(self, test_id: str) -> list[ResultRecord]:
        records: list[ResultRecord] = []
        for path in (self.store.root / "logs" / test_id).glob("*/result.json"):
            try:
                records.append(self.store.load(path))
            except (ValueError, TypeError):
                continue
        return sorted(records, key=lambda item: item.timestamp, reverse=True)


MkDocsReporter = MarkdownReporter
__all__ = ["MarkdownReporter", "MkDocsReporter"]
