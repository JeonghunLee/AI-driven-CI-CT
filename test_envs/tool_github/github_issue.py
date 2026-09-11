from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from test_envs.tool_github.issue_parser import issue_configuration


def _credentials(
    repository: str | None = None,
    token: str | None = None,
) -> tuple[str, str]:
    repo = repository or os.getenv("GITHUB_REPOSITORY")
    auth = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not repo or not auth:
        raise RuntimeError("GITHUB_REPOSITORY and GH_TOKEN/GITHUB_TOKEN are required")
    if repo.count("/") != 1:
        raise ValueError("GITHUB_REPOSITORY must use owner/repository format")
    return repo, auth


def _get(url: str, token: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-driven-ci-ct",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def get_issue(
    issue_number: int,
    repository: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    if issue_number < 1:
        raise ValueError("issue_number must be positive")
    repo, auth = _credentials(repository, token)
    value = _get(f"https://api.github.com/repos/{repo}/issues/{issue_number}", auth)
    if not isinstance(value, dict) or "pull_request" in value:
        raise ValueError(f"GitHub item #{issue_number} is not an Issue")
    return value


def local_mcp_requests(
    state: str = "open",
    limit: int = 20,
    repository: str | None = None,
    token: str | None = None,
) -> list[dict[str, object]]:
    if state not in {"open", "closed", "all"}:
        raise ValueError("state must be open, closed, or all")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    repo, auth = _credentials(repository, token)
    query = urlencode({"state": state, "labels": "test-request-runner", "per_page": limit})
    values = _get(f"https://api.github.com/repos/{repo}/issues?{query}", auth)
    requests: list[dict[str, object]] = []
    for issue in values:
        if "pull_request" in issue:
            continue
        try:
            config = issue_configuration(issue)
        except ValueError:
            continue
        if config["execution_host"] != "Local MCP":
            continue
        requests.append(
            {
                "number": issue["number"],
                "title": issue.get("title", ""),
                "url": issue.get("html_url", ""),
                "configuration": config,
            }
        )
    return requests
