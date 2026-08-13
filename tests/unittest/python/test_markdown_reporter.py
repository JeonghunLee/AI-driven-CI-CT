import unittest
from pathlib import Path

from tools.deepseek import Analysis
from tools.mkdocs_reporter import MarkdownReporter
from tools.result_normalizer import ResultRecord, ResultStore


class MarkdownReporterTests(unittest.TestCase):
    def test_markdown_first_report_contains_required_sections(self) -> None:
        root = "reports/test-artifacts/markdown-reporter"
        result = ResultRecord(
            "CT-MD-001",
            "PASS",
            "timing",
            0.2,
            description="UART timing",
            environment="test",
            equipment="Saleae",
            interface="UART",
            metrics={"jitter": 0.001},
        )
        ResultStore(root).save(result)
        path = MarkdownReporter(root).generate(result, Analysis("Stable", "passed", 1.0, "test"))
        text = path.read_text(encoding="utf-8")
        self.assertIn("## DeepSeek analysis", text)
        self.assertIn("## Warnings", text)
        self.assertIn("## Test history", text)

    def test_mkdocs_publish_preserves_each_execution(self) -> None:
        reports_root = "reports/test-artifacts/multi-execution-reports"
        docs_root = "reports/test-artifacts/multi-execution-docs"
        reporter = MarkdownReporter(reports_root, docs_root)
        analysis = Analysis("Stable", "passed", 1.0, "test")
        first = ResultRecord("CT-MD-HISTORY", "PASS", "timing", 0.1, execution_id="20260101-000001")
        second = ResultRecord("CT-MD-HISTORY", "FAIL", "timing", 0.2, execution_id="20260101-000002")

        ResultStore(reports_root).save(first)
        reporter.generate(first, analysis, publish_docs=True)
        ResultStore(reports_root).save(second)
        reporter.generate(second, analysis, publish_docs=True)

        base = Path(docs_root) / "test" / "ct" / "timing"
        self.assertTrue((base / "CT-MD-HISTORY" / "20260101-000001.md").exists())
        self.assertTrue((base / "CT-MD-HISTORY" / "20260101-000002.md").exists())
        latest = (base / "CT-MD-HISTORY.md").read_text(encoding="utf-8")
        self.assertIn("**FAIL**", latest)
        self.assertIn("## Execution documents", latest)
        self.assertIn("20260101-000001", latest)
        self.assertIn("20260101-000002", latest)
        index = (Path(docs_root) / "index.md").read_text(encoding="utf-8")
        self.assertIn("| timing | `CT-MD-HISTORY` |", index)
        self.assertIn("20260101-000001", index)
        self.assertIn("20260101-000002", index)
        self.assertFalse((Path(docs_root) / "test" / "index.md").exists())


if __name__ == "__main__":
    unittest.main()
