from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultRecord, ResultStore


def _safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(values: dict[str, Any]) -> str:
    rows = "\n".join(f"| {_safe(key)} | {_safe(value)} |" for key, value in values.items())
    return f"| Item | Value |\n|---|---|\n{rows or '| - | None |'}"


def _named_table(name: Any, values: dict[str, Any]) -> str:
    rows = "\n".join(f"| {_safe(key)} | {_safe(value)} |" for key, value in values.items())
    return f"| {_safe(name)} | Value |\n|---|---|\n{rows or '| - | None |'}"


def _warning_severity(warning_count: int) -> str:
    if warning_count >= 6:
        return "CRITICAL"
    if warning_count >= 4:
        return "HIGH"
    if warning_count >= 2:
        return "MEDIUM"
    return "LOW"

#
# Update Mdocs Markdown 
#       A. docs/tests/pytest/index.md , CT-USB-001.md,                               
#       B. docs/tests/unittest/index.md
#
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
        markdown_group = "unittest" if result.category.lower() == "unit" else result.test_id
        destination = self.store.root / "markdown" / markdown_group / f"{result.execution_id}_result.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.render(result, analysis, important_logs), encoding="utf-8")
        if publish_docs:
            self.publish(destination, result)
        return destination

    def publish(self, source: Path, result: ResultRecord) -> Path:
        report_type = "unittest" if result.category.lower() == "unit" else "pytest"
        target_dir = self.docs_root / "tests" / report_type
        target_dir.mkdir(parents=True, exist_ok=True)
        if report_type == "unittest":
            target = target_dir / f"{result.execution_id}.md"
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            self.update_indexes()
            return target
        latest_target = target_dir / f"{result.test_id}.md"

        canonical_dir = self.store.root / "markdown" / result.test_id
        for canonical in canonical_dir.glob("*_result.md"):
            execution_id = canonical.stem.removesuffix("_result")
            (target_dir / f"{result.test_id}__{execution_id}.md").write_text(
                canonical.read_text(encoding="utf-8"), encoding="utf-8"
            )

        #
        # target_dir
        # docs/test/pytest
        #       - CT-USB-001.md /CT-UART-001.md            
        #
        latest_content = source.read_text(encoding="utf-8")
        history = self.render_history(result.test_id, target_dir)
        latest_target.write_text(
            f"{history}\n",
            encoding="utf-8",
        )
        self.update_indexes()
        return target_dir / f"{result.test_id}__{result.execution_id}.md"

    def update_indexes(self) -> tuple[Path, Path]:
        test_root = self.docs_root / "tests"
        ct_rows: list[str] = []
        ct_execution_rows: list[tuple[str, str, str, str]] = []
        execution_categories: dict[tuple[str, str], str] = {}
        unit_execution_rows: list[tuple[str, str, int, int, int, str, str]] = []
        unittest_dir = test_root / "unittest"
        seen_unit_executions: set[str] = set()
        for result_path in self.store.result_paths():
            try:
                stored_result = self.store.load(result_path)
            except (ValueError, TypeError):
                continue
            execution_categories[(stored_result.test_id, stored_result.execution_id)] = stored_result.category
            if stored_result.category.lower() == "unit":
                link = f"{stored_result.execution_id}.md"
                if stored_result.execution_id in seen_unit_executions or not (unittest_dir / link).is_file():
                    continue
                seen_unit_executions.add(stored_result.execution_id)
                summary = stored_result.to_dict()["summary"]
                unit_execution_rows.append(
                    (
                        stored_result.execution_id,
                        stored_result.status,
                        int(summary["total"]),
                        int(summary["passed"]),
                        int(summary["failed"]) + int(summary["errors"]),
                        link,
                        stored_result.timestamp,
                    )
                )

        pytest_dir = test_root / "pytest"
        pytest_dir.mkdir(parents=True, exist_ok=True)
        unittest_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(pytest_dir.glob("*.md")):
            if path.name == "index.md":
                continue
            link = path.name
            if "__" in path.stem:
                test_id, execution_id = path.stem.split("__", 1)
                category = execution_categories.get((test_id, execution_id), "unknown")
                ct_execution_rows.append((execution_id, category, test_id, link))
                continue
            test_id = path.stem
            count = len(list(pytest_dir.glob(f"{test_id}__*.md")))
            result_paths = self.store.result_paths(test_id)
            latest_result = (
                self.store.load(max(result_paths, key=lambda item: item.name)) if result_paths else None
            )
            mode = latest_result.test_mode if latest_result else "unknown"
            category = latest_result.category if latest_result else "unknown"
            latest_date = latest_result.timestamp.partition("T")[0] if latest_result else "unknown"
            ct_rows.append(
                f"| {_safe(category)} | [`{_safe(test_id)}`]({link}) | {_safe(mode)} | "
                f"{_safe(latest_date)} | {count} |"
            )

        if unit_execution_rows:
            latest_unit = max(unit_execution_rows, key=lambda item: item[0])
            unit_summary = (
                f"| {latest_unit[2]} | {_safe(latest_unit[1])} | "
                f"[{_safe(latest_unit[6].partition('T')[0])}]({latest_unit[5]}) |"
            )
        else:
            unit_summary = "| 0 | - | - |"
#
# Recent Executions Section for Pytest
# Max: 100
        ct_recent = "\n".join(
            f"| [`{_safe(execution_id)}`]({link}) | {_safe(category)} | `{_safe(test_id)}` |"
            for execution_id, category, test_id, link in sorted(
                ct_execution_rows, key=lambda item: item[0], reverse=True
            )[:100]
        ) or "| - | - | - |"
#
# Recent Executions Section for Unit Tests
# Max: 100
        unit_recent = "\n".join(
            f"| [`{execution_id}`]({link}) | {_safe(status)} | {total} | {passed} | {failed} |"
            for execution_id, status, total, passed, failed, link, _timestamp in sorted(
                unit_execution_rows, key=lambda item: item[0], reverse=True
            )[:100]
        ) or "| - | - | 0 | 0 | 0 |"
        pytest_index = f"""# Pytest Results Index

* **VSCode-Task**
     * REPORT-Mkdocs: Generate Markdown to Pytest/Unittest 

<br/>

## Continuous Tests

<br/>

Find **Test ID** History for the test results below .

<br/>

| Category | Test ID | Mode | Latest | Execution Count |
|---|---|---|---|---:|
{chr(10).join(ct_rows) or '| - | - | - | - | 0 |'}

## Recent Executions

<br/>

* **Pytest Test History**   
Find **Execution ID** History for test results below (Max: 100).

<br/>

| Execution ID | Category | Test ID |
|---|---|---|
{ct_recent}
"""
        unittest_index = f"""# Unittest Results Index

* **VSCode-Task**
     * REPORT-Mkdocs: Generate Markdown to Pytest/Unittest 

<br/>

## Unit Tests

<br/>

* Latest **Execution ID** Summary   
Unittest Function Count : Tests 

<br/>

| Unittest Function Count | Pass | Latest |
|---:|---|---|
{unit_summary}

## Recent Executions

<br/>

* **Unittest Test History**       
Find **Execution ID** History for test results below (Max: 100).

<br/>

| Execution ID | Result | Tests | Passed | Failed |
|---|---|---:|---:|---:|
{unit_recent}
"""
        pytest_destination = test_root / "pytest" / "index.md"
        unittest_destination = test_root / "unittest" / "index.md"
        pytest_destination.write_text(pytest_index, encoding="utf-8")
        unittest_destination.write_text(unittest_index, encoding="utf-8")
        return pytest_destination, unittest_destination

#
# docs/test/pytest
#       - CT-USB-001.md /CT-UART-001.md            
#
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
        #
        # target_dir
        # docs/test/pytest
        #       - CT-USB-001.md /CT-UART-001.md            
        #

        #latest_target = target_dir / f"{test_id}.md"
        #if latest_target.is_file():
        #    history = latest_target.read_text(encoding="utf-8").partition("## Test History")[2]
        #    for row in history.splitlines():
        #        match = re.search(r"\[([^]]+)\]\([^)]*\)", row)
        #        if match:
       #             rows.setdefault(match.group(1), row)
        rendered_rows = (
            "\n".join(rows[key] for key in sorted(rows, reverse=True))
            or "| - | - | - | - | - | - | - | - |"
        )
        return f"""## Test History

<br/>
    
only Pytest `{test_id}` Test History , find the latest execution records below.    

Go Back to the [Pytest TEST All Index](./index.md)   

<br/>

| Date | Time | Execution ID | Commit | Branch | Result | Duration (s) | Environment |
|---|---|---|---|---|---|---:|---|
{rendered_rows}"""

    def render(self, result: ResultRecord, analysis: Analysis, important_logs: list[str] | None = None) -> str:
        if result.category.lower() == "unit":
            return self._render_unittest(result, analysis, important_logs)
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
        fixture_id = result.configuration.get("fixture_id", result.fixture_id or "None")
        test_configs = _named_table(
            "Test Item",
            {
                "Test ID": result.test_id,
                "Category": result.configuration.get("category", result.category),
                "Fixture ID": fixture_id,
                "Fixture mode": result.configuration.get("fixture_mode", result.test_mode),
            },
        )
        fixture_configs = _named_table(
            fixture_id,
            {
                "Interface": result.interface,
                "Equipment": result.equipment,
                "Equipment mode": result.equipment_mode,
                "Interface mode": result.interface_mode,
            },
        )
        test_source = _table({"Commit": result.commit, "Branch": result.branch})
        measurements = _table(dict(result.metrics))
        statistics = _table(dict(result.statistics))
        log_table = _table({"Test log": result.logs.get("main", "None"), "Test Result": result.execution_id + "_result.json"})
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
        #
        # Each Pytest Test Result
        #
        return f"""# {result.test_id} Test Result

Go Back to the [Pytest TEST All Index](./index.md)   

<br/> 

## Test summary

<br/>

{test_summary}

<br/>

### Test configs

<br/>

{test_configs}

<br/>

{fixture_configs}

### Test Source

<br/>

{test_source}

<br/>

### Measurement

<br/>

{measurements}

<br/>

### Statistics

<br/>

{statistics}

<br/>

### Logs

<br/>

* Path:    
  test_envs/reports/results/pytest/test_cases/{result.test_id}

<br/>

{log_table}

<br/>

## Local LLM Analysis

<br/>

{analysis_table}

<br/>

### LLM Test Prompt

<br/>

```
{_safe(analysis.prompt) or "Not configured"}
```

<br/>

### Test Result

<br/>

{analysis_result}

<br/>

### Test Summary

<br/>

{analysis_summary}
"""

    def _render_unittest(
        self,
        result: ResultRecord,
        analysis: Analysis,
        important_logs: list[str] | None = None,
    ) -> str:
        payload = result.to_dict()
        summary = payload["summary"]
        function_paths = {
            id(item): str(PurePosixPath(str(item.get("path", "unknown"))).parent)
            for item in result.test_functions
        }
        paths = list(dict.fromkeys(function_paths[id(item)] for item in result.test_functions))
        path_indexes = {path: index for index, path in enumerate(paths)}
        path_list = "\n".join(
            ["* Unit TEST"] + [f"    * PATH{index}: `{_safe(path)}`" for index, path in enumerate(paths)]
        )
        function_rows = "\n".join(
            f"| {path_indexes[function_paths[id(item)]]} | {_safe(item.get('function', 'unknown'))} | "
            f"{'PASS' if item.get('pass') else 'FAIL'} | "
            f"{float(item.get('duration', 0.0)):.6f} |"
            for item in result.test_functions
        ) or "| - | - | - | 0.000000 |"
        failed_rows = "\n".join(
            f"| {_safe(item.get('function', 'unknown'))} | {_safe(item.get('status', 'ERROR'))} | "
            f"{_safe(item.get('failure', '')) or 'No failure detail'} |"
            for item in result.test_functions
            if not item.get("pass") and item.get("status") != "SKIP"
        ) or "| - | - | None |"
        execution_summary = _table(
            {
                "Execution ID": result.execution_id,
                "Pass": result.status,
                "Latest": result.timestamp,
                "Duration": f"{result.duration:.6f} seconds",
                "Total": summary["total"],
                "Passed": summary["passed"],
                "Failed": summary["failed"],
                "Errors": summary["errors"],
                "Skipped": summary["skipped"],
            }
        )
        return f"""# unittest Result

## Test Summary

{execution_summary}

### Test Functions

{path_list}

| PATH | Test Function | Pass | Duration (s) |
|---:|---|---|---:|
{function_rows}

### Failed Functions

| Test Function | Status | Failure |
|---|---|---|
{failed_rows}

### Test Source

{_table({'Commit': result.commit, 'Branch': result.branch})}

### Logs

{_table({'Result log': result.logs.get('main', 'None'), 'Result json': f'{result.execution_id}_result.json'})}
"""


MkDocsReporter = MarkdownReporter
__all__ = ["MarkdownReporter", "MkDocsReporter"]
