from __future__ import annotations

from pathlib import Path
from typing import Any

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultRecord, ResultStore


def _safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _items(values: dict[str, Any]) -> str:
    return "\n".join(f"- **{_safe(key)}:** {_safe(value)}" for key, value in values.items()) or "- None"


def _report_mode(path: Path) -> str:
    prefix = "- **Test mode:**"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return "unknown"


def _report_category(path: Path) -> str:
    prefix = "- **Category:**"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return "unknown"


class MarkdownReporter:
    """Create the canonical human-readable report and optionally publish it to MkDocs."""

    def __init__(self, reports_root: str | Path = "test_envs/reports", docs_root: str | Path = "docs") -> None:
        self.store = ResultStore(reports_root)
        self.docs_root = Path(docs_root)

    def generate(
        self,
        result: ResultRecord,
        analysis: Analysis,
        important_logs: list[str] | None = None,
        publish_docs: bool = False,
    ) -> Path:
        destination = self.store.root / "markdown" / result.test_id / f"{result.execution_id}_result.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.render(result, analysis, important_logs), encoding="utf-8")
        if publish_docs:
            self.publish(destination, result)
        return destination

    def publish(self, source: Path, result: ResultRecord) -> Path:
        report_type = "unittest" if result.category.lower() == "unit" else "pytest"
        target_dir = self.docs_root / "tests" / report_type
        target_dir.mkdir(parents=True, exist_ok=True)
        latest_target = target_dir / f"{result.test_id}.md"

        canonical_dir = self.store.root / "markdown" / result.test_id
        for canonical in canonical_dir.glob("*_result.md"):
            execution_id = canonical.stem.removesuffix("_result")
            (target_dir / f"{result.test_id}__{execution_id}.md").write_text(
                canonical.read_text(encoding="utf-8"), encoding="utf-8"
            )

        snapshots = sorted(
            target_dir.glob(f"{result.test_id}__*.md"), key=lambda path: path.stem, reverse=True
        )
        links = "\n".join(
            f"- [{path.stem.split('__', 1)[1]}]({path.name})" for path in snapshots
        )
        latest_content = source.read_text(encoding="utf-8")
        latest_target.write_text(
            f"{latest_content}\n## Execution documents\n\n{links or '- None'}\n",
            encoding="utf-8",
        )
        self.update_indexes()
        return target_dir / f"{result.test_id}__{result.execution_id}.md"

    def update_indexes(self) -> tuple[Path, Path]:
        test_root = self.docs_root / "tests"
        ct_rows: list[str] = []
        unit_rows: list[str] = []
        ct_execution_rows: list[tuple[str, str]] = []
        unit_execution_rows: list[tuple[str, str]] = []

        for report_type in ("pytest", "unittest"):
            report_dir = test_root / report_type
            report_dir.mkdir(parents=True, exist_ok=True)
            for path in sorted(report_dir.glob("*.md")):
                if path.name == "index.md":
                    continue
                link = path.name
                if "__" in path.stem:
                    execution_id = path.stem.split("__", 1)[1]
                    target = unit_execution_rows if report_type == "unittest" else ct_execution_rows
                    target.append((execution_id, link))
                    continue
                test_id = path.stem
                count = len(list(report_dir.glob(f"{test_id}__*.md")))
                mode = _report_mode(path)
                if report_type == "unittest":
                    unit_rows.append(f"| `{_safe(test_id)}` | {_safe(mode)} | [Open]({link}) | {count} |")
                else:
                    category = _report_category(path)
                    if category == "unknown":
                        result_paths = self.store.result_paths(test_id)
                        if result_paths:
                            category = self.store.load(max(result_paths, key=lambda item: item.name)).category
                    ct_rows.append(
                        f"| {_safe(category)} | `{_safe(test_id)}` | {_safe(mode)} | [Open]({link}) | {count} |"
                    )

        ct_recent = "\n".join(
            f"- [`{execution_id}`]({link})"
            for execution_id, link in sorted(ct_execution_rows, key=lambda item: item[0], reverse=True)[:20]
        ) or "- None"
        unit_recent = "\n".join(
            f"- [`{execution_id}`]({link})"
            for execution_id, link in sorted(unit_execution_rows, key=lambda item: item[0], reverse=True)[:20]
        ) or "- None"
        pytest_index = f"""# pytest Results

## Continuous Tests

| Category | Test ID | Mode | Latest | Executions |
|---|---|---|---|---:|
{chr(10).join(ct_rows) or '| - | - | - | - | 0 |'}

## Recent Executions

{ct_recent}
"""
        unittest_index = f"""# unittest Results

## Unit Tests

| Test ID | Mode | Latest | Executions |
|---|---|---|---:|
{chr(10).join(unit_rows) or '| - | - | - | 0 |'}

## Recent Executions

{unit_recent}
"""
        pytest_destination = test_root / "pytest" / "index.md"
        unittest_destination = test_root / "unittest" / "index.md"
        pytest_destination.write_text(pytest_index, encoding="utf-8")
        unittest_destination.write_text(unittest_index, encoding="utf-8")
        return pytest_destination, unittest_destination

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
- **Category:** {_safe(result.category)}
- **Environment:** {_safe(result.environment)}
- **Configuration:** {_safe(dict(result.configuration))}
- **Test mode:** {_safe(result.test_mode)}
- **Equipment:** {_safe(result.equipment)}
- **Equipment mode:** {_safe(result.equipment_mode)}
- **Interface:** {_safe(result.interface)}
- **Interface mode:** {_safe(result.interface_mode)}
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

## Local LLM analysis

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
        for path in self.store.result_paths(test_id):
            try:
                records.append(self.store.load(path))
            except (ValueError, TypeError):
                continue
        return sorted(records, key=lambda item: item.timestamp, reverse=True)


MkDocsReporter = MarkdownReporter
__all__ = ["MarkdownReporter", "MkDocsReporter"]
