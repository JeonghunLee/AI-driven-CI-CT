from tools.issue_parser import parse_issue_body


def test_parse_issue_form_markdown() -> None:
    body = """### Test Type

pytest / CT

### Test Category

Timing
"""
    assert parse_issue_body(body) == {"Test Type": "pytest / CT", "Test Category": "Timing"}
