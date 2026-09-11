import unittest
from pathlib import Path
from unittest.mock import patch

from test_envs.tools.local_llm import Analysis
from test_envs.tool_github.github_reporter import (
    load_markdown_report,
    markdown_report_path,
    render_comment,
    render_environment_comment,
)
from test_envs.tools.result_normalizer import ResultRecord


class ReportingTests(unittest.TestCase):
    def test_github_reporter_reuses_canonical_markdown(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/github-markdown")
        result = ResultRecord(
            "CT-UART-001",
            "PASS",
            "timing",
            0.1,
            execution_id="20260911_010203_000001",
        )
        path = markdown_report_path(result, root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Existing Test Report\n\n| Test envs | Value |", encoding="utf-8")

        self.assertEqual(load_markdown_report(result, root), path.read_text(encoding="utf-8"))

    def test_issue_comment_contains_summary_and_evidence(self) -> None:
        result = ResultRecord("CT-001", "FAIL", "timing", 1.25, metrics={"jitter": 0.03})
        comment = render_comment(result, Analysis("Threshold exceeded", "timing", 0.9, "test"))
        self.assertIn("**Result: FAIL**", comment)
        self.assertIn("| Test envs | Value |", comment)
        self.assertIn("| test_environment | local |", comment)
        self.assertIn("| test_request | local_vscode |", comment)
        self.assertIn("Threshold exceeded", comment)
        self.assertIn("jitter: 0.03", comment)

    def test_unittest_comment_uses_unittest_paths_without_llm(self) -> None:
        result = ResultRecord(
            "UNIT-TEST",
            "PASS",
            "unit",
            0.25,
            execution_id="20260904_120000_000001",
        )
        comment = render_comment(result, Analysis("Unit tests passed", "unittest", 1.0, "not-used"))
        self.assertIn("Local LLM analyzer: Not used", comment)
        self.assertIn("docs/tests/unittest/20260904_120000_000001.md", comment)
        self.assertIn("test_reports/markdown/unittest/20260904_120000_000001_result.md", comment)

    def test_pytest_comment_uses_test_cases_markdown_path(self) -> None:
        result = ResultRecord(
            "CT-UART-001",
            "PASS",
            "interface",
            0.25,
            execution_id="20260904_120000_000002",
        )
        comment = render_comment(result, Analysis("Passed", "passed", 1.0, "test"))

        self.assertIn(
            "test_reports/markdown/pytest/test_cases/CT-UART-001/20260904_120000_000002_result.md",
            comment,
        )
        self.assertIn("Fixture ID: FIXTURE-001", comment)
        self.assertIn("Default Fixture Mode: mock", comment)
        self.assertIn("Test Path: test_envs/tests/pytest/test_cases/test_fixture_001_uart_timing.py", comment)

    def test_environment_comment_contains_detected_runner_values(self) -> None:
        check = {
            "os": {"detected": "linux", "name": "Linux-test"},
            "python": {"installed": True, "version": "3.12.0", "executable": "/python"},
            "ollama": {"installed": False, "available": False, "endpoint": "http://127.0.0.1:11434"},
        }
        environment = {
            "REQUESTED_TEST_ENVIRONMENT": "GitHub-hosted Runner",
            "REQUESTED_TEST_OS": "ubuntu",
            "TEST_ENVIRONMENT": "github_hosted_runner",
            "TEST_OS": "ubuntu",
            "TEST_REQUEST": "github_issue",
            "RUNNER_NAME": "GitHub Actions 1",
            "RUNNER_OS": "Linux",
            "RUNNER_ARCH": "X64",
        }
        with patch.dict("os.environ", environment, clear=False):
            comment = render_environment_comment(check)
        self.assertIn("**Result: CHECKED**", comment)
        self.assertIn("Requested environment: `GitHub-hosted Runner`", comment)
        self.assertIn("Type: `github_hosted_runner`", comment)
        self.assertIn("| test_os | ubuntu |", comment)
        self.assertIn("| test_name | GitHub Actions 1 |", comment)
        self.assertIn("| test_request | github_issue |", comment)
        self.assertIn("Version: `3.12.0`", comment)
        self.assertIn("API available: `False`", comment)


if __name__ == "__main__":
    unittest.main()
