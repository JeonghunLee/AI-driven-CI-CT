import unittest
from pathlib import Path


class RepositoryStructureTests(unittest.TestCase):
    def test_top_level_structure(self) -> None:
        self.assertTrue(Path("docs").is_dir())
        for name in ("configs", "tests", "reports", "tools"):
            self.assertTrue((Path("test_envs") / name).is_dir())
        for name in ("config", "configs", "tests", "reports", "tools"):
            self.assertFalse(Path(name).exists())

    def test_configuration_structure(self) -> None:
        root = Path("test_envs/configs")
        self.assertTrue((root / "unittest/config.json").is_file())
        self.assertTrue((root / "unittest/check.json").is_file())
        for group in ("test_cases", "test_equipments", "test_interfaces"):
            self.assertTrue((root / "pytest" / group / "catalog.json").is_file())
            self.assertFalse((Path("test_envs/tests/pytest") / group / "catalog.json").exists())

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

    def test_report_structure(self) -> None:
        root = Path("test_envs/reports")
        for relative in ("pytest/test_cases", "unittest", "pandoc", "markdown"):
            self.assertTrue((root / relative).is_dir())


if __name__ == "__main__":
    unittest.main()
