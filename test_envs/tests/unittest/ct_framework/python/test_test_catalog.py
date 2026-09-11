import json
import unittest
from pathlib import Path

from test_envs.tools.test_catalog import CATALOG_PATH, catalog_tests, discover_tests


class TestCatalogTests(unittest.TestCase):
    def test_generated_catalog_matches_python_ct_markers(self) -> None:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(catalog["version"], 1)
        self.assertTrue(catalog["generated_date"])
        self.assertEqual(catalog["tests"], discover_tests())
        for test in catalog["tests"]:
            self.assertEqual(
                list(test),
                [
                    "test_id",
                    "category",
                    "fixture_id",
                    "default_fixture_mode",
                    "test_prompt",
                    "test_path",
                ],
            )

    def test_static_consumers_match_catalog_test_ids(self) -> None:
        test_ids = [test["test_id"] for test in catalog_tests()]
        tasks = Path(".vscode/tasks.json").read_text(encoding="utf-8")
        issue_template = Path(".github/ISSUE_TEMPLATE/pytest_request.yml").read_text(encoding="utf-8")
        workflow = Path(".github/workflows/continuous-test.yml").read_text(encoding="utf-8")

        for test_id in test_ids:
            self.assertIn(f'"{test_id}"', tasks)
            self.assertIn(f"        - {test_id}", issue_template)
        self.assertIn(f"options: [{', '.join(test_ids)}]", workflow)

    def test_duplicate_test_ids_are_rejected(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/duplicate-test-catalog")
        root.mkdir(parents=True, exist_ok=True)
        source = """import pytest

@pytest.mark.ct(test_id=\"CT-DUPLICATE-001\", category=\"test\", fixture_id=\"FIXTURE-TEST\", fixture_mode=\"mock\")
def test_duplicate():
    pass
"""
        (root / "test_first.py").write_text(source, encoding="utf-8")
        (root / "test_second.py").write_text(source, encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Duplicate TEST ID"):
            discover_tests(root)


if __name__ == "__main__":
    unittest.main()
