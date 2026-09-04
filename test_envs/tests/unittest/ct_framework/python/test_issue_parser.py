import json
import unittest
from unittest.mock import patch

from test_envs.tools.issue_parser import event_configuration, parse_issue_body, request_configuration


class IssueParserTests(unittest.TestCase):
    def test_parse_issue_form_markdown(self) -> None:
        body = """### Runner

GitHub-hosted Linux
"""
        self.assertEqual(parse_issue_body(body), {"Runner": "GitHub-hosted Linux"})

    def test_parse_current_pytest_request(self) -> None:
        body = """### Test ID

CT-USB-001

### Fixture Mode

mock

### Runner

Linux

### Branch / Tag / Commit

feature/test

### Test Coverage

HTML coverage report

### Report Outputs

- [x] Pandoc HTML
- [ ] Pandoc DOCX
"""
        value = request_configuration(parse_issue_body(body))
        self.assertEqual(value["test_id"], "CT-USB-001")
        self.assertEqual(value["fixture_mode"], "mock")
        self.assertEqual(value["runner"], "GitHub-hosted Linux")
        self.assertEqual(value["runner_labels"], '["ubuntu-latest"]')
        self.assertEqual(value["request_ref"], "feature/test")
        self.assertEqual(value["test_type"], "Pytest")
        self.assertEqual(value["report_mkdocs"], "false")
        self.assertEqual(value["report_html"], "true")
        self.assertEqual(value["report_docx"], "false")

    def test_runner_selection_maps_to_github_labels(self) -> None:
        expected = {
            "GitHub-hosted Linux": '["ubuntu-latest"]',
            "GitHub-hosted Windows": '["windows-latest"]',
            "Self-hosted HIL Linux": '["self-hosted","linux","hw-test"]',
            "Self-hosted HIL Windows": '["self-hosted","windows","hw-test"]',
            "Default": '["ubuntu-latest"]',
            "Linux": '["ubuntu-latest"]',
            "Windows": '["windows-latest"]',
        }
        for runner, labels in expected.items():
            with self.subTest(runner=runner):
                self.assertEqual(request_configuration({"runner": runner})["runner_labels"], labels)

    def test_self_hosted_runner_requires_an_os(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported runner"):
            request_configuration({"runner": "Self-hosted HIL"})

    def test_environment_check_is_detected_from_issue_title(self) -> None:
        event = {
            "issue": {
                "title": "[TEST-CHECK] hosted Linux",
                "body": "### Runner\n\nGitHub-hosted Linux",
                "labels": [],
            }
        }
        with patch("test_envs.tools.issue_parser.Path.read_text", return_value=json.dumps(event)):
            value = event_configuration("event.json")
        self.assertEqual(value["request_kind"], "environment-check")
        self.assertEqual(value["runner_labels"], '["ubuntu-latest"]')

    def test_unittest_request_is_detected_from_issue_title(self) -> None:
        event = {
            "issue": {
                "title": "[UNITTEST-REQUEST] framework",
                "body": "### Unittest Scope\n\nCT Framework Python\n\n### Runner\n\nGitHub-hosted Windows",
                "labels": [],
            }
        }
        with patch("test_envs.tools.issue_parser.Path.read_text", return_value=json.dumps(event)):
            value = event_configuration("event.json")
        self.assertEqual(value["test_type"], "Unittest")
        self.assertEqual(value["unittest_target"], "test_envs/tests/unittest")
        self.assertEqual(value["runner_labels"], '["windows-latest"]')


if __name__ == "__main__":
    unittest.main()
