import unittest
from pathlib import Path

from test_envs.tools.result_normalizer import ResultRecord, ResultStore
from test_envs.tools.test_result import pending_result_paths, publish_latest


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


if __name__ == "__main__":
    unittest.main()
