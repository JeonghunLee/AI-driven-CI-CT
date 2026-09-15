import json
import unittest
from unittest.mock import patch

from test_envs.tool_github.issue_parser import event_configuration, parse_issue_body, request_configuration


class IssueParserTests(unittest.TestCase):
    def test_parse_issue_form_markdown(self) -> None:
        body = """### Test Environment

GitHub-hosted Runner
"""
        self.assertEqual(parse_issue_body(body), {"Test Environment": "GitHub-hosted Runner"})

    def test_parse_current_pytest_request(self) -> None:
        body = """### Test ID

CT-USB-001

### Fixture Mode

mock

### Test Environment

GitHub-hosted Runner

### Operating System

Ubuntu

### Branch / Tag / Commit

feature/test

### Test Coverage

HTML coverage report

### Report Outputs

- [x] Log
- [x] Markdown
- [x] Pandoc HTML
- [ ] Pandoc DOCX
"""
        value = request_configuration(parse_issue_body(body))
        self.assertEqual(value["test_id"], "CT-USB-001")
        self.assertEqual(value["fixture_mode"], "mock")
        self.assertEqual(value["execution_host"], "GitHub-hosted Runner")
        self.assertEqual(value["test_environment"], "github_hosted_runner")
        self.assertEqual(value["test_os"], "ubuntu")
        self.assertEqual(value["runner_labels"], '["ubuntu-latest"]')
        self.assertEqual(value["request_ref"], "feature/test")
        self.assertEqual(value["test_type"], "Pytest")
        self.assertEqual(value["report_log"], "true")
        self.assertEqual(value["report_markdown"], "true")
        self.assertEqual(value["report_mkdocs"], "false")
        self.assertEqual(value["report_html"], "true")
        self.assertEqual(value["report_docx"], "false")

    def test_environment_and_os_map_to_github_labels(self) -> None:
        expected = {
            ("GitHub-hosted Runner", "Ubuntu"): '["ubuntu-latest"]',
            ("GitHub-hosted Runner", "Windows"): '["windows-latest"]',
            ("Self-hosted Runner", "Ubuntu"): '["self-hosted","linux","hw-test"]',
            ("Self-hosted Runner", "Windows"): '["self-hosted","windows","hw-test"]',
        }
        for (environment, test_os), labels in expected.items():
            with self.subTest(environment=environment, test_os=test_os):
                value = request_configuration(
                    {"test_environment": environment, "test_os": test_os}
                )
                self.assertEqual(value["runner_labels"], labels)

    def test_legacy_combined_runner_is_still_readable(self) -> None:
        value = request_configuration({"runner": "GitHub-hosted Windows"})
        self.assertEqual(value["execution_host"], "GitHub-hosted Runner")
        self.assertEqual(value["test_os"], "windows")
        self.assertEqual(value["runner_labels"], '["windows-latest"]')

    def test_unknown_pytest_id_is_rejected_by_catalog(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported TEST ID"):
            request_configuration({"test_type": "Pytest", "test_id": "CT-UNKNOWN-999"})

    def test_markdown_and_mkdocs_publication_are_separate_outputs(self) -> None:
        markdown = request_configuration({"reports": "- [x] Markdown"})
        mkdocs = request_configuration({"reports": "- [x] MkDocs Markdown"})

        self.assertEqual(markdown["report_markdown"], "true")
        self.assertEqual(markdown["report_mkdocs"], "false")
        self.assertEqual(mkdocs["report_markdown"], "false")
        self.assertEqual(mkdocs["report_mkdocs"], "true")

    def test_unknown_environment_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported test environment"):
            request_configuration({"test_environment": "Unknown"})

    def test_local_mcp_is_not_a_github_issue_environment(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported test environment"):
            request_configuration(
                {"test_environment": "Local MCP", "test_os": "Windows"}
            )

    def test_github_hosted_runner_rejects_pytest_hil(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not support Pytest HIL"):
            request_configuration(
                {
                    "test_type": "Pytest",
                    "fixture_mode": "hil",
                    "test_environment": "GitHub-hosted Runner",
                    "test_os": "Ubuntu",
                }
            )

    def test_self_hosted_runner_accepts_pytest_hil(self) -> None:
        value = request_configuration(
            {
                "test_type": "Pytest",
                "fixture_mode": "hil",
                "test_environment": "Self-hosted Runner",
                "test_os": "Windows",
            }
        )
        self.assertEqual(value["fixture_mode"], "hil")
        self.assertEqual(value["test_environment"], "self_hosted_runner")

    def test_github_hosted_rejects_marker_resolved_hil(self) -> None:
        entry = {
            "test_id": "CT-HIL-001",
            "default_fixture_mode": "hil",
        }
        with patch(
            "test_envs.tool_github.issue_parser.catalog_tests", return_value=[entry]
        ), patch(
            "test_envs.tool_github.issue_parser.catalog_by_id",
            return_value={"CT-HIL-001": entry},
        ):
            with self.assertRaisesRegex(ValueError, "does not support Pytest HIL"):
                request_configuration(
                    {
                        "test_type": "Pytest",
                        "test_id": "CT-HIL-001",
                        "fixture_mode": "marker",
                        "test_environment": "GitHub-hosted Runner",
                        "test_os": "Ubuntu",
                    }
                )

    def test_environment_check_is_detected_from_issue_title(self) -> None:
        event = {
            "issue": {
                "title": "[TEST-CHECK] hosted Linux",
                "body": "### Test Environment\n\nGitHub-hosted Runner\n\n### Operating System\n\nUbuntu",
                "labels": [],
            }
        }
        with patch("test_envs.tool_github.issue_parser.Path.read_text", return_value=json.dumps(event)):
            value = event_configuration("event.json")
        self.assertEqual(value["request_kind"], "environment-check")
        self.assertEqual(value["runner_labels"], '["ubuntu-latest"]')

    def test_unittest_request_is_detected_from_issue_title(self) -> None:
        event = {
            "issue": {
                "title": "[UNITTEST-REQUEST] framework",
                "body": "### Unittest Scope\n\nCT Framework Python\n\n### Test Environment\n\nGitHub-hosted Runner\n\n### Operating System\n\nWindows",
                "labels": [],
            }
        }
        with patch("test_envs.tool_github.issue_parser.Path.read_text", return_value=json.dumps(event)):
            value = event_configuration("event.json")
        self.assertEqual(value["test_type"], "Unittest")
        self.assertEqual(value["unittest_target"], "test_envs/tests/unittest")
        self.assertEqual(value["runner_labels"], '["windows-latest"]')


if __name__ == "__main__":
    unittest.main()
