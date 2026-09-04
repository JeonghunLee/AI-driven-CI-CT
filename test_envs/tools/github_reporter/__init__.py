from __future__ import annotations

import json
import os
from typing import Any
from urllib.request import Request, urlopen

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultRecord


def render_comment(result: ResultRecord, analysis: Analysis) -> str:
    def rows(values: dict[str, Any]) -> str:
        return "\n".join(f"- {key}: {value}" for key, value in values.items()) or "- None"

    repository = os.getenv("GITHUB_REPOSITORY", "owner/repository")
    run_id = os.getenv("GITHUB_RUN_ID")
    artifact = f"https://github.com/{repository}/actions/runs/{run_id}" if run_id else "Available in the workflow run"
    report_type = "unittest" if result.category.lower() == "unit" else "pytest"
    is_unittest = report_type == "unittest"
    mkdocs_name = f"{result.execution_id}.md" if is_unittest else f"{result.test_id}.md"
    mkdocs_source = f"docs/tests/{report_type}/{mkdocs_name}"
    markdown_group = "unittest" if is_unittest else result.test_id
    warnings = "\n".join(
        f"- {item.get('severity', 'Important')}: {item.get('message', '')}" for item in analysis.warnings
    ) or "- None"
    return f"""## Test Result

**Result: {result.status}**

### Test
- ID: {result.test_id}
- Category: {result.category}
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
- Markdown result: `test_envs/reports/markdown/{markdown_group}/{result.execution_id}_result.md`
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


__all__ = ["post_comment", "render_comment"]
