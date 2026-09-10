import unittest
from pathlib import Path

from test_envs.tools.pandoc_reporter import _default_output_dir, convert, latest_markdown


class PandocReporterTests(unittest.TestCase):
    def test_pytest_output_is_grouped_under_test_cases(self) -> None:
        source = Path("test_envs/reports/markdown/pytest/test_cases/CT-UART-001/execution_result.md")

        self.assertEqual(
            _default_output_dir(source),
            Path("test_envs/reports/pandocs/pytest/test_cases/CT-UART-001"),
        )

    def test_unittest_output_is_grouped_separately(self) -> None:
        source = Path("test_envs/reports/markdown/unittest/execution_result.md")

        self.assertEqual(
            _default_output_dir(source),
            Path("test_envs/reports/pandocs/unittest"),
        )

    def test_latest_markdown_searches_nested_report_groups(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/latest-markdown")
        older = root / "markdown/unittest/20260101_000000_000001_result.md"
        latest = root / "markdown/pytest/test_cases/CT-UART-001/20260102_000000_000001_result.md"
        older.parent.mkdir(parents=True, exist_ok=True)
        latest.parent.mkdir(parents=True, exist_ok=True)
        older.write_text("older", encoding="utf-8")
        latest.write_text("latest", encoding="utf-8")

        self.assertEqual(latest_markdown(root), latest)

    def test_pandoc_rejects_unknown_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported"):
            convert("missing.md", "odt")


if __name__ == "__main__":
    unittest.main()
