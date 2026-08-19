import unittest
from pathlib import Path

from test_envs.tools.local_llm import Analysis
from test_envs.tools.mkdocs_reporter import MarkdownReporter, _warning_severity
from test_envs.tools.result_normalizer import ResultRecord, ResultStore


class MarkdownReporterTests(unittest.TestCase):
    def test_markdown_first_report_contains_required_sections(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/markdown-reporter")
        result = ResultRecord(
            "CT-MD-001",
            "PASS",
            "timing",
            0.2,
            description="UART timing",
            environment="test",
            configuration={
                "category": "timing",
                "fixture_id": "FIXTURE-001",
                "fixture_mode": "mock",
            },
            fixture_id="FIXTURE-001",
            equipment="Saleae",
            equipment_mode="mock",
            interface="UART",
            interface_mode="mock",
            metrics={"jitter": 0.001},
        )
        ResultStore(root).save(result)
        path = MarkdownReporter(root).generate(
            result,
            Analysis(
                "Stable",
                "information_security",
                0.85,
                "ollama/deepseek-r1:7b",
                warnings=[{"severity": "Important", "message": "Review configuration."}],
                recommendations="Improve error handling.",
                prompt="Analyze the test result.",
            ),
        )
        text = path.read_text(encoding="utf-8")
        self.assertIn("## Local LLM Analysis", text)
        self.assertIn("### LLM Test Prompt", text)
        self.assertIn("### Test Result", text)
        self.assertIn("### Test Summary", text)
        self.assertIn("### Test Source", text)
        self.assertIn("### Test configs", text)
        self.assertIn("| Commit |", text)
        self.assertIn("| Branch |", text)
        self.assertNotIn("## Test history", text)
        self.assertIn("| Test Item | Value |", text)
        self.assertIn("| Test ID | CT-MD-001 |", text)
        self.assertIn("| Fixture ID | FIXTURE-001 |", text)
        self.assertIn("<br/>", text)
        self.assertIn("| FIXTURE-001 | Value |", text)
        self.assertIn("| Interface | UART |", text)
        self.assertIn("| Equipment | Saleae |", text)
        self.assertIn("| Equipment mode | mock |", text)
        self.assertIn("| Interface mode | mock |", text)
        self.assertIn("| Status | enabled |", text)
        self.assertIn("| **Status** | PASS |", text)
        self.assertIn("| **Severity** | LOW |", text)
        self.assertIn("| **Warnings** | 1 |", text)
        self.assertIn("| **Needs Escalation** | OFF |", text)
        self.assertIn("| Recommendations | Improve error handling. |", text)

    def test_warning_count_controls_severity(self) -> None:
        expected = {
            0: "LOW",
            1: "LOW",
            2: "MEDIUM",
            3: "MEDIUM",
            4: "HIGH",
            5: "HIGH",
            6: "CRITICAL",
            20: "CRITICAL",
        }
        for warning_count, severity in expected.items():
            with self.subTest(warning_count=warning_count):
                self.assertEqual(_warning_severity(warning_count), severity)

    def test_mkdocs_publish_preserves_each_execution(self) -> None:
        reports_root = Path("test_envs/tests/.tmp/ct_framework/multi-execution-reports")
        docs_root = Path("test_envs/tests/.tmp/ct_framework/multi-execution-docs")
        reporter = MarkdownReporter(reports_root, docs_root)
        root_index = Path(docs_root) / "index.md"
        root_index.parent.mkdir(parents=True, exist_ok=True)
        root_index.write_text("# System Overview", encoding="utf-8")
        analysis = Analysis("Stable", "passed", 1.0, "test")
        first = ResultRecord("CT-MD-HISTORY", "PASS", "timing", 0.1, execution_id="20260101-000001")
        second = ResultRecord(
            "CT-MD-HISTORY",
            "FAIL",
            "timing",
            0.2,
            test_mode="hil",
            execution_id="20260101-000002",
        )

        ResultStore(reports_root).save(first)
        reporter.generate(first, analysis, publish_docs=True)
        ResultStore(reports_root).save(second)
        reporter.generate(second, analysis, publish_docs=True)

        unit_result = ResultRecord(
            "UNIT-INTERNAL-001",
            "PASS",
            "unit",
            0.05,
            description="test_result_parser",
            execution_id="20260101-000003",
        )
        ResultStore(reports_root).save(unit_result)
        reporter.generate(unit_result, analysis, publish_docs=True)

        base = Path(docs_root) / "tests" / "pytest"
        self.assertTrue((base / "CT-MD-HISTORY__20260101-000001.md").exists())
        self.assertTrue((base / "CT-MD-HISTORY__20260101-000002.md").exists())
        latest = (base / "CT-MD-HISTORY.md").read_text(encoding="utf-8")
        self.assertIn("| Result | FAIL |", latest)
        self.assertIn("## Test History", latest)
        self.assertIn("| Date | Time | Execution ID | Commit | Branch |", latest)
        history = latest.partition("## Test History")[2]
        self.assertIn(f"| {first.commit[:7]} |", history)
        self.assertNotIn(f"| {first.commit} |", history)
        self.assertNotIn("## Execution documents", latest)
        self.assertIn(
            "[20260101-000001](CT-MD-HISTORY__20260101-000001.md)",
            latest,
        )
        self.assertIn("20260101-000001", latest)
        self.assertIn("20260101-000002", latest)
        pytest_index = (Path(docs_root) / "tests/pytest/index.md").read_text(encoding="utf-8")
        unittest_index = (Path(docs_root) / "tests/unittest/index.md").read_text(encoding="utf-8")
        self.assertIn("<br/>", pytest_index)
        self.assertIn("| Category | Test ID | Mode | Latest | Execution Count |", pytest_index)
        self.assertIn("| timing | [`CT-MD-HISTORY`](CT-MD-HISTORY.md) | hil |", pytest_index)
        self.assertIn(second.timestamp.partition("T")[0], pytest_index)
        self.assertIn("20260101-000001", pytest_index)
        self.assertIn("20260101-000002", pytest_index)
        self.assertIn("| Execution ID | Category | Test ID |", pytest_index)
        self.assertIn(
            "| [`20260101-000002`](CT-MD-HISTORY__20260101-000002.md) | timing | `CT-MD-HISTORY` |",
            pytest_index,
        )
        self.assertIn("# unittest Results", unittest_index)
        self.assertIn(
            "| Test Function | Pass | Latest | Test Function Count |",
            unittest_index,
        )
        self.assertIn(
            "| [test_result_parser](UNIT-INTERNAL-001.md) | PASS |",
            unittest_index,
        )
        self.assertNotIn("| Test ID | Mode |", unittest_index)
        self.assertEqual(root_index.read_text(encoding="utf-8"), "# System Overview")


if __name__ == "__main__":
    unittest.main()
