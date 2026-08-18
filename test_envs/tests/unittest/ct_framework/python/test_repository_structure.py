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
        self.assertTrue((root / "config.json").is_file())
        self.assertTrue((root / "check.json").is_file())
        self.assertTrue((root / "unittest").is_dir())
        self.assertFalse((root / "pytest").exists())

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

    def test_pytest_case_structure(self) -> None:
        root = Path("test_envs/tests/pytest/test_cases")
        expected = {
            "test_fixture_001_uart_timing.py",
            "test_fixture_002_usb_loopback.py",
            "test_fixture_003_network_loopback.py",
        }
        self.assertEqual({path.name for path in root.glob("test_*.py")}, expected)
        for name in ("communication", "timing", "functional", "performance", "stability", "regression"):
            self.assertFalse((root / name).exists())

    def test_pytest_fixture_structure(self) -> None:
        root = Path("test_envs/tests/pytest/fixtures")
        for name in (
            "fixture_001_uart_saleae.py",
            "fixture_002_usb_digilent.py",
            "fixture_003_network.py",
            "fixture_004_jtag_fpga.py",
            "fixture_005_full_hil.py",
        ):
            self.assertTrue((root / name).is_file())

    def test_report_structure(self) -> None:
        root = Path("test_envs/reports")
        for relative in ("pytest/test_cases", "unittest", "pandoc", "markdown"):
            self.assertTrue((root / relative).is_dir())


if __name__ == "__main__":
    unittest.main()
