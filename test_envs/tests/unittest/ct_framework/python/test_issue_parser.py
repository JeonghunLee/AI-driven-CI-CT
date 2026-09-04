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
        self.assertEqual(value["runner"], "GitHub-hosted Linux")
        self.assertEqual(value["runner_labels"], '["ubuntu-latest"]')
        self.assertEqual(value["request_ref"], "feature/test")
        self.assertEqual(value["report_mkdocs"], "true")
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


if __name__ == "__main__":
    unittest.main()
