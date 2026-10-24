import json
import unittest
from pathlib import Path
from unittest.mock import patch

from test_envs.tools.pandoc_reporter import (
    REFERENCE_CONFIG,
    REFERENCE_DOC,
    pandoc_executable,
    additional_docx_args,
    _default_output_dir,
    convert,
    latest_markdown,
)


class PandocReporterTests(unittest.TestCase):
    def test_reference_document_is_stored_outside_test_reports(self) -> None:
        self.assertEqual(REFERENCE_DOC, Path("docx/reference/reference.docx"))

    def test_reference_manifest_describes_the_editable_document(self) -> None:
        manifest = json.loads(REFERENCE_CONFIG.read_text(encoding="utf-8"))

        self.assertEqual(Path(manifest["reference_docx"]), REFERENCE_DOC)
        self.assertTrue(manifest["editor"]["instruction"])
        self.assertTrue(manifest["pandoc"]["docx_uses_reference_docx"])
        self.assertFalse(manifest["pandoc"]["html_uses_reference_docx"])

    def test_additional_docx_args_exclude_dynamic_report_paths(self) -> None:
        args = additional_docx_args()

        self.assertIn("--toc", args)
        self.assertIn("--lua-filter=docx/lua/test_result.lua", args)
        self.assertNotIn("--reference-doc", args)
        self.assertNotIn("-o", args)

    def test_pytest_output_is_grouped_under_test_cases(self) -> None:
        source = Path("test_reports/markdown/pytest/test_cases/CT-UART-001/execution_result.md")

        self.assertEqual(
            _default_output_dir(source),
            Path("test_reports/pandocs/pytest/test_cases/CT-UART-001"),
        )

    def test_unittest_output_is_grouped_separately(self) -> None:
        source = Path("test_reports/markdown/unittest/execution_result.md")

        self.assertEqual(
            _default_output_dir(source),
            Path("test_reports/pandocs/unittest"),
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

    def test_pandoc_falls_back_to_the_windows_per_user_install(self) -> None:
        with patch("test_envs.tools.pandoc_reporter.shutil.which", return_value=None), patch(
            "test_envs.tools.pandoc_reporter.os.getenv", return_value="C:/Users/test/AppData/Local"
        ), patch("test_envs.tools.pandoc_reporter.Path.is_file", return_value=True):
            executable = pandoc_executable()

        self.assertEqual(executable, "C:\\Users\\test\\AppData\\Local\\Pandoc\\pandoc.exe")

    def test_docx_conversion_uses_reference_document(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/pandoc-reference")
        source = root / "source.md"
        reference = root / "reference.docx"
        output = root / "output"
        root.mkdir(parents=True, exist_ok=True)
        source.write_text("# Report", encoding="utf-8")
        reference.write_bytes(b"reference")

        with patch("test_envs.tools.pandoc_reporter.shutil.which", return_value="pandoc"), patch(
            "test_envs.tools.pandoc_reporter.REFERENCE_DOC", reference
        ), patch("test_envs.tools.pandoc_reporter.subprocess.run") as run:
            destination = convert(source, "docx", output)

        self.assertEqual(destination, output / "source.docx")
        command = run.call_args.args[0]
        self.assertEqual(command[-2:], ["--reference-doc", str(reference)])

    def test_html_conversion_does_not_use_reference_document(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/pandoc-html")
        source = root / "source.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# Report", encoding="utf-8")

        with patch("test_envs.tools.pandoc_reporter.shutil.which", return_value="pandoc"), patch(
            "test_envs.tools.pandoc_reporter.subprocess.run"
        ) as run:
            convert(source, "html", root / "output")

        self.assertNotIn("--reference-doc", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
