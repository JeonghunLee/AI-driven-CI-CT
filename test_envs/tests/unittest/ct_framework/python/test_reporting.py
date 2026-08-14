import unittest

from test_envs.tools.local_llm import Analysis
from test_envs.tools.github_reporter import render_comment
from test_envs.tools.result_normalizer import ResultRecord


class ReportingTests(unittest.TestCase):
    def test_issue_comment_contains_summary_and_evidence(self) -> None:
        result = ResultRecord("CT-001", "FAIL", "timing", 1.25, metrics={"jitter": 0.03})
        comment = render_comment(result, Analysis("Threshold exceeded", "timing", 0.9, "test"))
        self.assertIn("**Result: FAIL**", comment)
        self.assertIn("Threshold exceeded", comment)
        self.assertIn("jitter: 0.03", comment)


if __name__ == "__main__":
    unittest.main()
