from __future__ import annotations

import os
import platform
from typing import Literal

from mcp.server import MCPServer

from test_envs.mcp_server.runner import (
    ROOT,
    TestRequest,
    all_test_lists,
    pytest_test_list,
    run_all_tests,
    run_test,
    test_environment,
    unittest_test_list,
    update_latest,
    update_mkdocs as publish_latest_to_mkdocs,
)
from test_envs.tool_github.github_issue import get_issue, local_mcp_requests
from test_envs.tool_github.github_reporter import post_comment
from test_envs.tool_github.issue_parser import issue_configuration


mcp = MCPServer(
    "AI-driven CI-CT",
    instructions=(
        "Inspect the environment and allowlisted tests before execution. "
        "Pytest HIL requires PYTEST_HIL_ALLOW=true. MkDocs publication requires MKDOC_UPDATE=true."
    ),
)


@mcp.tool()
def get_test_envs() -> dict[str, object]:
    """Check OS, Python/venv, Ollama/model, Pandoc, and MCP permission flags."""
    return test_environment()


@mcp.tool()
def get_test_list_pytest() -> dict[str, object]:
    """List allowlisted Pytest TEST IDs, source paths, fixture modes, and HIL availability."""
    return pytest_test_list()


@mcp.tool()
def get_test_list_unittest() -> dict[str, object]:
    """List allowlisted Unittest scopes and discovered test files."""
    return unittest_test_list()


@mcp.tool()
def get_test_list_all() -> dict[str, object]:
    """List all Pytest and Unittest targets plus coverage and report options."""
    return all_test_lists()


@mcp.tool()
def get_github_issue_requests(
    state: Literal["open", "closed", "all"] = "open",
    limit: int = 20,
) -> dict[str, object]:
    """List GitHub test-request Issues assigned to this runner-free Local MCP."""
    return {"requests": local_mcp_requests(state=state, limit=limit)}


@mcp.tool()
def run_github_issue(
    issue_number: int,
    timeout_seconds: int = 3600,
) -> dict[str, object]:
    """Read one Local MCP GitHub Issue, run it locally, and post its canonical Markdown."""
    issue = get_issue(issue_number)
    config = issue_configuration(issue)
    if config["request_kind"] != "test":
        raise ValueError("run_github_issue supports Pytest and Unittest request Issues")
    if config["execution_host"] != "Local MCP":
        raise ValueError("The Issue Test Environment must be Local MCP")
    local_os = "windows" if platform.system().lower() == "windows" else "ubuntu"
    if config["test_os"] != local_os:
        raise RuntimeError(
            f"Issue requests {config['test_os']}, but this Local MCP host is {local_os}"
        )
    pandoc = (
        "both"
        if config["report_docx"] == "true" and config["report_html"] == "true"
        else "docx"
        if config["report_docx"] == "true"
        else "html"
        if config["report_html"] == "true"
        else "none"
    )
    coverage = {
        "Terminal missing-lines report": "terminal",
        "HTML coverage report": "html",
    }.get(config["coverage"], "none")
    if config["test_type"] == "Pytest":
        request = TestRequest(
            test_type="pytest",
            test_id=config["test_id"],
            fixture_mode=config["fixture_mode"],
            coverage=coverage,
            markdown=True,
            pandoc=pandoc,
        )
    else:
        scope = "ct_framework_python" if config["unittest_scope"] == "CT Framework Python" else "all"
        request = TestRequest(
            test_type="unittest",
            unittest_scope=scope,
            coverage=coverage,
            markdown=True,
            pandoc=pandoc,
        )
    result = run_test(
        request,
        timeout_seconds,
        environment={
            "TEST_REQUEST": "github_issue",
            "TEST_ENVIRONMENT": "local",
            "TEST_OS": local_os,
            "TEST_NAME": os.getenv("TEST_NAME", "local_01"),
        },
    )
    markdown = result.get("reports", {}).get("markdown")
    if not markdown:
        raise RuntimeError("The test did not generate the canonical Markdown report")
    body = (ROOT / str(markdown)).read_text(encoding="utf-8")
    post_comment(issue_number, body)
    result["github_issue"] = {
        "number": issue_number,
        "url": issue.get("html_url", ""),
        "comment_source": markdown,
    }
    return result


@mcp.tool()
def run_test_pytest(
    test_id: str,
    fixture_mode: Literal["marker", "mock", "hil"] = "marker",
    coverage: Literal["none", "terminal", "html"] = "none",
    markdown: bool = True,
    pandoc: Literal["none", "docx", "html", "both"] = "none",
    timeout_seconds: int = 3600,
) -> dict[str, object]:
    """Run one allowlisted Pytest CT and return normalized result and report paths."""
    return run_test(
        TestRequest(
            test_type="pytest",
            test_id=test_id,
            fixture_mode=fixture_mode,
            coverage=coverage,
            markdown=markdown,
            pandoc=pandoc,
        ),
        timeout_seconds,
    )


@mcp.tool()
def run_test_unittest(
    scope: Literal["all", "ct_framework_python", "python", "c_cpp", "firmware", "common"] = "all",
    coverage: Literal["none", "terminal", "html"] = "none",
    markdown: bool = True,
    pandoc: Literal["none", "docx", "html", "both"] = "none",
    timeout_seconds: int = 3600,
) -> dict[str, object]:
    """Run all Unittest tests, CT Framework Python, or another allowlisted extension scope."""
    return run_test(
        TestRequest(
            test_type="unittest",
            unittest_scope=scope,
            coverage=coverage,
            markdown=markdown,
            pandoc=pandoc,
        ),
        timeout_seconds,
    )


@mcp.tool()
def run_test_all(
    pytest_test_id: str = "",
    fixture_mode: Literal["marker", "mock", "hil"] = "marker",
    unittest_scope: Literal["all", "ct_framework_python", "python", "c_cpp", "firmware", "common"] = "all",
    coverage: Literal["none", "terminal", "html"] = "none",
    markdown: bool = True,
    pandoc: Literal["none", "docx", "html", "both"] = "none",
    timeout_seconds: int = 3600,
) -> dict[str, object]:
    """Run one Pytest CT and one Unittest scope sequentially."""
    return run_all_tests(
        test_id=pytest_test_id,
        fixture_mode=fixture_mode,
        unittest_scope=unittest_scope,
        coverage=coverage,
        markdown=markdown,
        pandoc=pandoc,
        timeout_seconds=timeout_seconds,
    )


@mcp.tool()
def update_latest_result(
    test_type: Literal["pytest", "unittest"],
    test_id: str = "",
    markdown: bool = True,
    pandoc: Literal["none", "docx", "html", "both"] = "none",
) -> dict[str, object]:
    """Read the latest result and log, and update Markdown or Pandoc DOCX/HTML outputs."""
    return update_latest(test_type, test_id, markdown, pandoc)


@mcp.tool()
def update_mkdocs(
    test_type: Literal["pytest", "unittest"],
    test_id: str = "",
) -> dict[str, object]:
    """Publish the latest generated Markdown to docs/tests when MKDOC_UPDATE=true."""
    return publish_latest_to_mkdocs(test_type, test_id)
