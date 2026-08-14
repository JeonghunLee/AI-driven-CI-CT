import unittest

from test_envs.tools.pandoc_reporter import convert


class PandocReporterTests(unittest.TestCase):
    def test_pandoc_rejects_unknown_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported"):
            convert("missing.md", "odt")


if __name__ == "__main__":
    unittest.main()
