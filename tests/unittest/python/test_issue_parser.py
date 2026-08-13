import unittest

from tools.issue_parser import parse_issue_body


class IssueParserTests(unittest.TestCase):
    def test_parse_issue_form_markdown(self) -> None:
        body = """### Test Type

pytest / CT

### Test Category

Timing
"""
        self.assertEqual(parse_issue_body(body), {"Test Type": "pytest / CT", "Test Category": "Timing"})


if __name__ == "__main__":
    unittest.main()
