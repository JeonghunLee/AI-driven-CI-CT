import unittest
from pathlib import Path

from test_result import publish_latest


class LatestResultTests(unittest.TestCase):
    def test_publish_latest_copies_markdown(self) -> None:
        root = Path("reports/test-artifacts/latest-result")
        source = root / "source.md"
        destination = root / "output" / "latest.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# latest", encoding="utf-8")
        self.assertEqual(publish_latest(source, destination), destination)
        self.assertEqual(destination.read_text(encoding="utf-8"), "# latest")


if __name__ == "__main__":
    unittest.main()
