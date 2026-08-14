import unittest
from pathlib import Path


class RepositoryStructureTests(unittest.TestCase):
    def test_top_level_structure(self) -> None:
        self.assertTrue(Path("docs").is_dir())
        for name in ("config", "tests", "reports", "tools"):
            self.assertTrue((Path("test_envs") / name).is_dir())
            self.assertFalse(Path(name).exists())

    def test_unittest_structure(self) -> None:
        root = Path("test_envs/tests/unittest")
        for relative in (
            "ct_framework/python",
            "python",
            "c_cpp",
            "firmware",
            "common",
        ):
            self.assertTrue((root / relative).is_dir())


if __name__ == "__main__":
    unittest.main()
