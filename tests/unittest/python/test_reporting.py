from tools.github_reporter import render_comment
from tools.deepseek import Analysis
from tools.result_normalizer import ResultRecord


def test_issue_comment_contains_summary_and_evidence() -> None:
    result = ResultRecord("CT-001", "FAIL", "timing", 1.25, metrics={"jitter": 0.03})
    comment = render_comment(result, Analysis("Threshold exceeded", "timing", 0.9, "test"))
    assert "**Result: FAIL**" in comment
    assert "Threshold exceeded" in comment
    assert "jitter: 0.03" in comment
