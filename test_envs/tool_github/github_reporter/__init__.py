from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultRecord
from test_envs.tools.test_catalog import catalog_by_id


def _test_envs_table(values: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {key} | {values.get(key, 'unknown')} |"
        for key in ("test_os", "test_name", "test_environment", "test_request")
    )
    return f"""| Test envs | Value |
|---|---|
{rows}"""


def markdown_report_path(result: ResultRecord, root: str | Path = "test_reports/markdown") -> Path:
    root_path = Path(root)
    if result.category.lower() == "unit":
        return root_path / "unittest" / f"{result.execution_id}_result.md"
    return root_path / "pytest" / "test_cases" / result.test_id / f"{result.execution_id}_result.md"


def load_markdown_report(result: ResultRecord, root: str | Path = "test_reports/markdown") -> str:
    path = markdown_report_path(result, root)
    if not path.is_file():
        raise FileNotFoundError(f"Canonical Markdown report does not exist: {path}")
    return path.read_text(encoding="utf-8")


def render_environment_comment(check: dict[str, Any]) -> str:
    requested_environment = os.getenv("REQUESTED_TEST_ENVIRONMENT", "unknown")
    requested_os = os.getenv("REQUESTED_TEST_OS", "unknown")
    inferred_environment = (
        "self_hosted_runner"
        if requested_environment == "Self-hosted Runner"
        else "github_hosted_runner"
        if requested_environment == "GitHub-hosted Runner"
        else "unknown"
    )
    runner_environment = os.getenv("TEST_ENVIRONMENT", inferred_environment)
    runner_name = os.getenv("RUNNER_NAME", "unknown")
    runner_os = os.getenv("RUNNER_OS", str(check.get("os", {}).get("detected", "unknown")))
    runner_arch = os.getenv("RUNNER_ARCH", "unknown")
    test_envs = {
        "test_os": os.getenv("TEST_OS", requested_os.lower()),
        "test_name": runner_name,
        "test_environment": runner_environment,
        "test_request": os.getenv("TEST_REQUEST", "github_issue"),
    }
    os_check = dict(check.get("os", {}))
    python_check = dict(check.get("python", {}))
    ollama_check = dict(check.get("ollama", {}))
    return f"""## Test Environment Check

**Result: CHECKED**

### Test envs

{_test_envs_table(test_envs)}

### Host
- Requested environment: `{requested_environment}`
- Requested OS: `{requested_os}`
- Type: `{runner_environment}`
- Runner: `{runner_name}`
- Runner OS: `{runner_os}`
- Architecture: `{runner_arch}`

### Operating System
- Detected: `{os_check.get('detected', 'unknown')}`
- Platform: `{os_check.get('name', 'unknown')}`

### Python
- Installed: `{python_check.get('installed', False)}`
- Version: `{python_check.get('version', 'unknown')}`
- Executable: `{python_check.get('executable', 'unknown')}`

### Ollama
- Installed: `{ollama_check.get('installed', False)}`
- API available: `{ollama_check.get('available', False)}`
- Version: `{ollama_check.get('version') or 'Not available'}`
- Endpoint: `{ollama_check.get('endpoint', 'unknown')}`
- Selected model: `{ollama_check.get('selected_model') or 'Not configured'}`
- Selected model installed: `{ollama_check.get('selected_model_installed', False)}`
"""


def render_comment(result: ResultRecord, analysis: Analysis) -> str:
    def rows(values: dict[str, Any]) -> str:
        return "\n".join(f"- {key}: {value}" for key, value in values.items()) or "- None"

    repository = os.getenv("GITHUB_REPOSITORY", "owner/repository")
    run_id = os.getenv("GITHUB_RUN_ID")
    artifact = f"https://github.com/{repository}/actions/runs/{run_id}" if run_id else "Available in the workflow run"
    report_type = "unittest" if result.category.lower() == "unit" else "pytest"
    is_unittest = report_type == "unittest"
    catalog_entry = {} if is_unittest else catalog_by_id().get(result.test_id, {})
    mkdocs_name = f"{result.execution_id}.md" if is_unittest else f"{result.test_id}.md"
    mkdocs_source = f"docs/tests/{report_type}/{mkdocs_name}"
    markdown_group = "unittest" if is_unittest else f"pytest/test_cases/{result.test_id}"
    warnings = "\n".join(
        f"- {item.get('severity', 'Important')}: {item.get('message', '')}" for item in analysis.warnings
    ) or "- None"
    return f"""## Test Result

**Result: {result.status}**

### Test envs

{_test_envs_table(dict(result.test_envs))}

### Test
- ID: {result.test_id}
- Category: {result.category}
- Fixture ID: {catalog_entry.get("fixture_id", "Not applicable")}
- Default Fixture Mode: {catalog_entry.get("default_fixture_mode", "Not applicable")}
- Test Path: {catalog_entry.get("test_path", "Not applicable")}
- Interface: {result.interface}
- Equipment: {result.equipment}
- Duration: {result.duration:.3f} seconds

### Measurement
{rows(dict(result.metrics))}

### Statistics
{rows(dict(result.statistics))}

### Warning Summary
{warnings}

### Analysis
{analysis.summary}

- Classification: {analysis.classification}
- Confidence: {analysis.confidence:.2f}
- Local LLM analyzer: {"Not used" if is_unittest else analysis.source}

### Evidence
- [Workflow run and artifacts]({artifact})
- MkDocs source: `{mkdocs_source}`
- Markdown result: `test_reports/markdown/{markdown_group}/{result.execution_id}_result.md`
- Commit: `{result.commit}`
- Branch: `{result.branch}`
- Runner: {result.runner}
- Execution ID: `{result.execution_id}`
"""


def post_comment(issue: int, body: str, repository: str | None = None, token: str | None = None) -> None:
    repo = repository or os.getenv("GITHUB_REPOSITORY")
    auth = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not repo or not auth:
        raise RuntimeError("GITHUB_REPOSITORY and GH_TOKEN/GITHUB_TOKEN are required")
    request = Request(
        f"https://api.github.com/repos/{repo}/issues/{issue}/comments",
        data=json.dumps({"body": body}).encode(),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {auth}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-driven-ci-ct",
        },
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        if response.status not in {200, 201}:
            raise RuntimeError(f"GitHub returned HTTP {response.status}")


__all__ = [
    "load_markdown_report",
    "markdown_report_path",
    "post_comment",
    "render_comment",
    "render_environment_comment",
]
