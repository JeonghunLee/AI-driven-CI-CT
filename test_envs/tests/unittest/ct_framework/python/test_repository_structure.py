import unittest
from pathlib import Path


class RepositoryStructureTests(unittest.TestCase):
    def test_top_level_structure(self) -> None:
        self.assertTrue(Path("docs").is_dir())
        for name in ("configs", "tests", "tools", "tool_github", "test_pipeline", "mcp_server"):
            self.assertTrue((Path("test_envs") / name).is_dir())
        self.assertTrue(Path("test_reports").is_dir())
        for name in ("config", "configs", "tests", "reports", "tools"):
            self.assertFalse(Path(name).exists())

    def test_configuration_structure(self) -> None:
        root = Path("test_envs/configs")
        self.assertTrue((root / "config.json").is_file())
        self.assertTrue((root / "check.json").is_file())
        self.assertFalse((root / "unittest").exists())
        self.assertFalse((root / "pytest").exists())

    def test_unittest_structure(self) -> None:
        root = Path("test_envs/tests/unittest")
        self.assertTrue((root / "conftest.py").is_file())
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
        root = Path("test_reports")
        for relative in (
            "results/pytest/test_cases",
            "results/unittest",
            "pandocs/pytest/test_cases",
            "pandocs/unittest",
            "markdown/pytest/test_cases",
            "markdown/unittest",
        ):
            self.assertTrue((root / relative).is_dir())
        self.assertFalse((root / "pandoc").exists())
        self.assertTrue((root / "pandocs/reference.docx").is_file())
        self.assertFalse(any((root / "markdown").glob("CT-*")))
        self.assertFalse((root / "results/unittest/.tmp").exists())
        self.assertFalse(any(path.name == "pytest" for path in (root / "results/unittest").rglob("*")))
        self.assertFalse((root / "pytest").exists())
        self.assertFalse((root / "unittest").exists())
        self.assertFalse(Path("test_envs/reports").exists())

    def test_role_specific_tool_packages(self) -> None:
        github_root = Path("test_envs/tool_github")
        self.assertTrue((github_root / "issue_parser.py").is_file())
        self.assertTrue((github_root / "github_reporter/__init__.py").is_file())
        pipeline_root = Path("test_envs/test_pipeline")
        self.assertTrue((pipeline_root / "environment_setup.py").is_file())
        self.assertTrue((pipeline_root / "pipeline.py").is_file())
        mcp_root = Path("test_envs/mcp_server")
        self.assertTrue((mcp_root / "runner.py").is_file())
        self.assertTrue((mcp_root / "server.py").is_file())
        for legacy in (
            "test_envs/tools/issue_parser.py",
            "test_envs/tools/github_reporter",
            "test_envs/tools/environment_setup.py",
            "test_envs/tools/pipeline.py",
        ):
            self.assertFalse(Path(legacy).exists())

    def test_docs_test_structure(self) -> None:
        root = Path("docs/tests")
        self.assertFalse(Path("docs/test").exists())
        self.assertEqual(
            {path.name for path in root.iterdir() if path.is_dir()},
            {"pytest", "unittest"},
        )
        self.assertFalse(any(path.is_dir() for path in root.glob("*/*")))
        self.assertTrue(all(path.suffix == ".md" for path in root.glob("*/*") if path.is_file()))


if __name__ == "__main__":
    unittest.main()
