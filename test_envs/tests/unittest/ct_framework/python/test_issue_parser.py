import unittest

from test_envs.tools.issue_parser import parse_issue_body, request_configuration


class IssueParserTests(unittest.TestCase):
    def test_parse_issue_form_markdown(self) -> None:
        body = """### Test Type

pytest / CT

### Test Category

Timing
"""
        self.assertEqual(parse_issue_body(body), {"Test Type": "pytest / CT", "Test Category": "Timing"})

    def test_parse_current_pytest_request(self) -> None:
        body = """### Test Type

pytest / CT

### Test Category

Communication

### Test ID

CT-USB-001

### Fixture Mode

mock

### Unittest Scope

Not applicable - Pytest CT

### Runner

Linux

### Branch / Tag / Commit

feature/test

### Test Coverage

HTML coverage report

### Report Outputs

- [x] MkDocs Markdown
- [x] Pandoc HTML
- [ ] Pandoc DOCX
"""
        value = request_configuration(parse_issue_body(body))
        self.assertEqual(value["test_id"], "CT-USB-001")
        self.assertEqual(value["fixture_mode"], "mock")
        self.assertEqual(value["runner_labels"], '["ubuntu-latest"]')
        self.assertEqual(value["request_ref"], "feature/test")
        self.assertEqual(value["report_mkdocs"], "true")
        self.assertEqual(value["report_html"], "true")
        self.assertEqual(value["report_docx"], "false")

    def test_runner_selection_maps_to_github_labels(self) -> None:
        expected = {
            "Default": '["ubuntu-latest"]',
            "Linux": '["ubuntu-latest"]',
            "Windows": '["windows-latest"]',
            "Self-hosted HIL": '["self-hosted","hw-test"]',
        }
        for runner, labels in expected.items():
            with self.subTest(runner=runner):
                self.assertEqual(request_configuration({"runner": runner})["runner_labels"], labels)


if __name__ == "__main__":
    unittest.main()
