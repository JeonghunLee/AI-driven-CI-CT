import unittest
from pathlib import Path

from test_envs.tools.local_llm import Analysis
from test_envs.tools.mkdocs_reporter import MarkdownReporter
from test_envs.tools.result_normalizer import ResultRecord, ResultStore


class MarkdownReporterTests(unittest.TestCase):
    def test_markdown_first_report_contains_required_sections(self) -> None:
        root = Path("test_envs/reports/unittest/.tmp/markdown-reporter")
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
        self.assertIn("## Local LLM analysis", text)
        self.assertIn("## Warnings", text)
        self.assertIn("## Test Source", text)
        self.assertIn("| Commit |", text)
        self.assertIn("| Branch |", text)
        self.assertNotIn("## Test history", text)
        self.assertIn("**Test mode:** mock", text)

    def test_mkdocs_publish_preserves_each_execution(self) -> None:
        reports_root = Path("test_envs/reports/unittest/.tmp/multi-execution-reports")
        docs_root = Path("test_envs/reports/unittest/.tmp/multi-execution-docs")
        reporter = MarkdownReporter(reports_root, docs_root)
        root_index = Path(docs_root) / "index.md"
        root_index.parent.mkdir(parents=True, exist_ok=True)
        root_index.write_text("# System Overview", encoding="utf-8")
        analysis = Analysis("Stable", "passed", 1.0, "test")
        first = ResultRecord("CT-MD-HISTORY", "PASS", "timing", 0.1, execution_id="20260101-000001")
        second = ResultRecord("CT-MD-HISTORY", "FAIL", "timing", 0.2, execution_id="20260101-000002")

        ResultStore(reports_root).save(first)
        reporter.generate(first, analysis, publish_docs=True)
        ResultStore(reports_root).save(second)
        reporter.generate(second, analysis, publish_docs=True)

        base = Path(docs_root) / "tests" / "pytest"
        self.assertTrue((base / "CT-MD-HISTORY__20260101-000001.md").exists())
        self.assertTrue((base / "CT-MD-HISTORY__20260101-000002.md").exists())
        latest = (base / "CT-MD-HISTORY.md").read_text(encoding="utf-8")
        self.assertIn("**FAIL**", latest)
        self.assertIn("## Test History", latest)
        self.assertIn("| Date | Time | Execution ID | Commit | Branch |", latest)
        self.assertIn(f"| {first.commit[:7]} |", latest)
        self.assertNotIn(f"| {first.commit} |", latest)
        self.assertNotIn("## Execution documents", latest)
        self.assertIn(
            "[20260101-000001](CT-MD-HISTORY__20260101-000001.md)",
            latest,
        )
        self.assertIn("20260101-000001", latest)
        self.assertIn("20260101-000002", latest)
        pytest_index = (Path(docs_root) / "tests/pytest/index.md").read_text(encoding="utf-8")
        unittest_index = (Path(docs_root) / "tests/unittest/index.md").read_text(encoding="utf-8")
        self.assertIn("| timing | `CT-MD-HISTORY` |", pytest_index)
        self.assertIn("(CT-MD-HISTORY.md)", pytest_index)
        self.assertIn("20260101-000001", pytest_index)
        self.assertIn("20260101-000002", pytest_index)
        self.assertIn("# unittest Results", unittest_index)
        self.assertEqual(root_index.read_text(encoding="utf-8"), "# System Overview")


if __name__ == "__main__":
    unittest.main()
