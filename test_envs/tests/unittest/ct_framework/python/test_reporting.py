import unittest
from unittest.mock import patch

from test_envs.tools.local_llm import Analysis
from test_envs.tools.github_reporter import render_comment, render_environment_comment
from test_envs.tools.result_normalizer import ResultRecord


class ReportingTests(unittest.TestCase):
    def test_issue_comment_contains_summary_and_evidence(self) -> None:
        result = ResultRecord("CT-001", "FAIL", "timing", 1.25, metrics={"jitter": 0.03})
        comment = render_comment(result, Analysis("Threshold exceeded", "timing", 0.9, "test"))
        self.assertIn("**Result: FAIL**", comment)
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
        self.assertIn("reports/markdown/unittest/20260904_120000_000001_result.md", comment)

    def test_environment_comment_contains_detected_runner_values(self) -> None:
        check = {
            "os": {"detected": "linux", "name": "Linux-test"},
            "hardware": {
                "machine": "x86_64",
                "processor": "cpu-test",
                "logical_cores": 4,
                "memory_bytes": 8 * 1024**3,
                "workspace_disk_total_bytes": 14 * 1024**3,
                "workspace_disk_free_bytes": 9 * 1024**3,
            },
            "python": {"installed": True, "version": "3.12.0", "executable": "/python"},
            "ollama": {"installed": False, "available": False, "endpoint": "http://127.0.0.1:11434"},
        }
        environment = {
            "REQUESTED_RUNNER": "GitHub-hosted Linux",
            "RUNNER_ENVIRONMENT": "github-hosted",
            "RUNNER_NAME": "GitHub Actions 1",
            "RUNNER_OS": "Linux",
            "RUNNER_ARCH": "X64",
        }
        with patch.dict("os.environ", environment, clear=False):
            comment = render_environment_comment(check)
        self.assertIn("**Result: CHECKED**", comment)
        self.assertIn("Requested: `GitHub-hosted Linux`", comment)
        self.assertIn("Type: `github-hosted`", comment)
        self.assertIn("Logical CPU cores: `4`", comment)
        self.assertIn("Physical memory: `8.00 GiB`", comment)
        self.assertIn("Version: `3.12.0`", comment)
        self.assertIn("API available: `False`", comment)

    def test_environment_comment_uses_unknown_for_missing_hardware_capacity(self) -> None:
        check = {"os": {}, "hardware": {"logical_cores": None}, "python": {}, "ollama": {}}
        with patch.dict("os.environ", {}, clear=False):
            comment = render_environment_comment(check)
        self.assertIn("Logical CPU cores: `unknown`", comment)
        self.assertIn("Workspace disk: `unknown`", comment)


if __name__ == "__main__":
    unittest.main()
