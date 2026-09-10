from __future__ import annotations

from typing import Literal

from mcp.server import MCPServer

from test_envs.mcp_server.runner import (
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
def run_test_pytest(
    test_id: Literal["CT-UART-001", "CT-USB-001", "CT-NETWORK-001"],
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
    pytest_test_id: Literal["CT-UART-001", "CT-USB-001", "CT-NETWORK-001"] = "CT-UART-001",
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
