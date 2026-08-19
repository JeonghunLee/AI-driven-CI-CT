from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultRecord, ResultStore


def _safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(values: dict[str, Any]) -> str:
    rows = "\n".join(f"| {_safe(key)} | {_safe(value)} |" for key, value in values.items())
    return f"| Item | Value |\n|---|---|\n{rows or '| - | None |'}"


def _warning_severity(warning_count: int) -> str:
    if warning_count >= 6:
        return "CRITICAL"
    if warning_count >= 4:
        return "HIGH"
    if warning_count >= 2:
        return "MEDIUM"
    return "LOW"


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

        latest_content = source.read_text(encoding="utf-8")
        history = self.render_history(result.test_id, target_dir)
        latest_target.write_text(
            f"{latest_content}\n{history}\n",
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
                result_paths = self.store.result_paths(test_id)
                latest_result = (
                    self.store.load(max(result_paths, key=lambda item: item.name))
                    if result_paths
                    else None
                )
                mode = latest_result.test_mode if latest_result else "unknown"
                if report_type == "unittest":
                    unit_rows.append(f"| `{_safe(test_id)}` | {_safe(mode)} | [Open]({link}) | {count} |")
                else:
                    category = latest_result.category if latest_result else "unknown"
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

    def render_history(self, test_id: str, target_dir: Path) -> str:
        records: list[ResultRecord] = []
        for path in self.store.result_paths(test_id):
            try:
                records.append(self.store.load(path))
            except (ValueError, TypeError):
                continue
        rows: dict[str, str] = {}
        for item in sorted(records, key=lambda value: value.timestamp, reverse=True):
            execution_file = f"{test_id}__{item.execution_id}.md"
            if not (target_dir / execution_file).is_file():
                continue
            date, separator, time = item.timestamp.partition("T")
            if not separator:
                date, time = item.timestamp, "unknown"
            rows[item.execution_id] = (
                f"| {_safe(date)} | {_safe(time)} | [{_safe(item.execution_id)}]({execution_file}) | "
                f"{_safe(item.commit[:7])} | {_safe(item.branch)} | {item.status} | "
                f"{item.duration:.3f} | {_safe(item.environment)} |"
            )
        latest_target = target_dir / f"{test_id}.md"
        if latest_target.is_file():
            history = latest_target.read_text(encoding="utf-8").partition("## Test History")[2]
            for row in history.splitlines():
                match = re.search(r"\[([^]]+)\]\([^)]*\)", row)
                if match:
                    rows.setdefault(match.group(1), row)
        rendered_rows = (
            "\n".join(rows[key] for key in sorted(rows, reverse=True))
            or "| - | - | - | - | - | - | - | - |"
        )
        return f"""## Test History

| Date | Time | Execution ID | Commit | Branch | Result | Duration (s) | Environment |
|---|---|---|---|---|---|---:|---|
{rendered_rows}"""

    def render(self, result: ResultRecord, analysis: Analysis, important_logs: list[str] | None = None) -> str:
        logs = "<br>".join(_safe(line) for line in (important_logs or [])) or "None"
        warnings = "<br>".join(_safe(item.get("message", "")) for item in analysis.warnings) or "None"
        warning_count = len(analysis.warnings)
        severity = _warning_severity(warning_count)
        test_summary = _table(
            {
                "Description": result.description,
                "Category": result.category,
                "Environment": result.environment,
                "Result": result.status,
                "Execution time": f"{result.duration:.3f} seconds",
                "Execution date": result.timestamp,
                "Execution ID": result.execution_id,
            }
        )
        test_configs = _table(
            {
                "Category": result.configuration.get("category", result.category),
                "Fixture ID": result.configuration.get("fixture_id", "None"),
                "Fixture mode": result.configuration.get("fixture_mode", result.test_mode),
                "Test mode": result.test_mode,
                "Equipment": result.equipment,
                "Equipment mode": result.equipment_mode,
                "Interface": result.interface,
                "Interface mode": result.interface_mode,
            }
        )
        test_source = _table({"Commit": result.commit, "Branch": result.branch})
        measurements = _table(dict(result.metrics))
        statistics = _table(dict(result.statistics))
        log_table = _table({"Test log": result.logs.get("main", "None"), "Important": logs})
        analysis_table = _table(
            {
                "Classification": analysis.classification,
                "Confidence": f"{analysis.confidence:.2f}",
                "Analyzer": analysis.source,
                "Status": "enabled" if analysis.source.startswith("ollama/") else "disabled",
            }
        )
        analysis_result = _table(
            {
                "**Status**": result.status,
                "**Severity**": severity,
                "**Warnings**": warning_count,
                "**Needs Escalation**": "ON" if analysis.needs_escalation else "OFF",
            }
        )
        analysis_summary = _table(
            {
                "Summary": analysis.summary,
                "Failure Analysis": analysis.failure_analysis or "Not applicable",
                "Source Review": analysis.source_review or "Not requested",
                "Warnings": warnings,
                "Recommendations": analysis.recommendations or "No recommendation provided.",
            }
        )
        return f"""# {result.test_id} Test Result

## Test summary

{test_summary}

### Test configs

{test_configs}

### Test Source

{test_source}

### Measurement

{measurements}

### Statistics

{statistics}

### Logs

{log_table}

## Local LLM Analysis

{analysis_table}

### LLM Test Prompt

{_safe(analysis.prompt) or "Not configured"}

### Test Result

{analysis_result}

### Test Summary

{analysis_summary}
"""


MkDocsReporter = MarkdownReporter
__all__ = ["MarkdownReporter", "MkDocsReporter"]
