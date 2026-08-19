import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from test_envs.tools.pipeline import run
from test_envs.tools.result_normalizer import ResultRecord, ResultStore
from test_envs.tools.test_result import _run_with_progress, pending_result_paths, publish_latest


class LatestResultTests(unittest.TestCase):
    def test_publish_latest_copies_markdown(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/latest-result")
        source = root / "source.md"
        destination = root / "output" / "latest.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# latest", encoding="utf-8")
        self.assertEqual(publish_latest(source, destination), destination)
        self.assertEqual(destination.read_text(encoding="utf-8"), "# latest")

    def test_pending_results_use_test_id_and_execution_id(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/pending-results")
        docs = Path("test_envs/tests/.tmp/ct_framework/pending-docs")
        store = ResultStore(root)
        complete = ResultRecord("CT-PENDING-001", "PASS", "timing", 0.1, execution_id="20260101_000001_000001")
        missing = ResultRecord("CT-PENDING-002", "PASS", "timing", 0.1, execution_id="20260101_000002_000002")
        complete_path = store.save(complete)
        missing_path = store.save(missing)
        complete_markdown = root / "markdown" / complete.test_id / f"{complete.execution_id}_result.md"
        complete_markdown.parent.mkdir(parents=True, exist_ok=True)
        complete_markdown.write_text("# complete", encoding="utf-8")
        missing_markdown = root / "markdown" / missing.test_id / f"{missing.execution_id}_result.md"
        missing_markdown.unlink(missing_ok=True)

        self.assertEqual(pending_result_paths(store=store, docs_root=docs), [missing_path])
        self.assertEqual(
            pending_result_paths(publish_docs=True, store=store, docs_root=docs),
            [complete_path, missing_path],
        )

    def test_pending_progress_prints_numeric_state(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = _run_with_progress(
                lambda: {"status": "ok"},
                index=2,
                total=3,
                test_id="CT-PROGRESS-001",
                execution_id="20260819_100000_000001",
            )
        self.assertEqual(result, {"status": "ok"})
        self.assertIn("[2/3] RUNNING 000s", output.getvalue())
        self.assertIn("[2/3] COMPLETE 000s", output.getvalue())

    def test_unittest_report_does_not_call_local_llm(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/unit-no-llm")
        store = ResultStore(root)
        record = ResultRecord(
            "unittest",
            "PASS",
            "unit",
            0.1,
            execution_id="20260101_030405_123456",
            test_functions=(
                {
                    "path": "test_envs/tests/unittest/python/test_sample.py",
                    "function": "test_sample",
                    "pass": True,
                    "status": "PASS",
                    "duration": 0.1,
                    "failure": "",
                },
            ),
        )
        result_path = store.save(record)
        with patch("test_envs.tools.pipeline.ResultStore", return_value=store), patch(
            "test_envs.tools.pipeline.LocalLLMAnalyzer",
            side_effect=AssertionError("Local LLM must not run for unittest"),
        ):
            output = run(result_path=result_path)
        self.assertEqual(output["local_llm_model"], "not-used")
        self.assertTrue(Path(output["markdown"]).is_file())
        self.assertFalse((root / "local_llm/20260101_030405_123456_local_llm.log").exists())

    def test_pending_unittest_uses_execution_id_without_test_id(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/pending-unit-results")
        docs = Path("test_envs/tests/.tmp/ct_framework/pending-unit-docs")
        store = ResultStore(root)
        record = ResultRecord(
            "unittest",
            "PASS",
            "unit",
            0.1,
            execution_id="20260101_010203_123456",
            test_functions=(
                {
                    "path": "test_envs/tests/unittest/python/test_example.py",
                    "function": "ExampleTests::test_ok",
                    "pass": True,
                    "status": "PASS",
                    "duration": 0.1,
                    "failure": "",
                },
            ),
        )
        result_path = store.save(record)
        markdown = root / "markdown/unittest/20260101_010203_123456_result.md"
        markdown.unlink(missing_ok=True)
        document = docs / "tests/unittest/20260101_010203_123456.md"
        document.unlink(missing_ok=True)
        self.assertEqual(pending_result_paths(store=store, docs_root=docs), [result_path])
        markdown.parent.mkdir(parents=True, exist_ok=True)
        markdown.write_text("# unittest Result", encoding="utf-8")
        self.assertEqual(pending_result_paths(store=store, docs_root=docs), [])
        self.assertEqual(
            pending_result_paths(publish_docs=True, store=store, docs_root=docs),
            [result_path],
        )


if __name__ == "__main__":
    unittest.main()
