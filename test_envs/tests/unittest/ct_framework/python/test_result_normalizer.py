import json
import unittest
from pathlib import Path

from test_envs.tools.result_normalizer import ResultRecord, ResultStore, from_junit


class ResultNormalizerTests(unittest.TestCase):
    def test_result_store_creates_canonical_result_and_logs(self) -> None:
        test_root = Path("test_envs/tests/.tmp/ct_framework/unit-result-store")
        record = ResultRecord("UT-NORMALIZER-001", "pass", "functional", 0.1)
        self.assertRegex(record.execution_id, r"^\d{8}_\d{6}_\d{6}$")
        path = ResultStore(test_root).save(record)
        payload = json.loads(path.read_text())
        self.assertEqual(payload["test_case"]["status"], "PASS")
        self.assertTrue(payload["test_src"]["commit"])
        self.assertTrue(payload["test_src"]["branch"])
        self.assertTrue(payload["test_result"]["timestamp"].endswith("+09:00"))
        self.assertEqual(ResultStore(test_root).latest(), path)
        self.assertEqual(path.name, f"{record.execution_id}_result.json")
        self.assertTrue((path.parent / record.logs["main"]).exists())
        self.assertEqual(record.logs, {"main": f"{record.execution_id}_test.log"})
        self.assertEqual(
            {
                item.name
                for item in path.parent.iterdir()
                if item.name.startswith(f"{record.execution_id}_")
            },
            {f"{record.execution_id}_result.json", f"{record.execution_id}_test.log"},
        )
        self.assertIn("metrics", payload["test_result"])
        self.assertIn("statistics", payload["test_result"])

    def test_result_rejects_unknown_status(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported"):
            ResultRecord("UT-001", "maybe", "functional", 0.0)

    def test_result_rejects_unknown_test_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "test_mode"):
            ResultRecord("UT-001", "PASS", "functional", 0.0, test_mode="invalid")

    def test_result_preserves_mock_hil_modes(self) -> None:
        result = ResultRecord(
            "CT-MODE-001",
            "PASS",
            "functional",
            0.1,
            fixture_id="FIXTURE-004",
            test_mode="hil",
            interfaces=("JTAG",),
            interface_mode="hil",
            equipments=("FPGA",),
            equipment_mode="hil",
            modes={"mock": {"enabled": True}, "hil": {"enabled": True}},
        )
        fixture_configs = result.to_dict()["fixture_configs"]
        self.assertEqual(fixture_configs["test_mode"], "hil")
        self.assertEqual(fixture_configs["interface_mode"], "hil")
        self.assertEqual(fixture_configs["equipment_mode"], "hil")
        self.assertEqual(fixture_configs["fixture_id"], "FIXTURE-004")
        self.assertEqual(fixture_configs["interfaces"], ["JTAG"])
        self.assertEqual(fixture_configs["equipments"], ["FPGA"])
        self.assertTrue(fixture_configs["modes"]["hil"]["enabled"])

    def test_junit_normalization(self) -> None:
        record = from_junit("test_envs/tests/fixtures/junit.xml", "UNIT-SAMPLE")
        self.assertEqual(record.status, "FAIL")
        self.assertEqual(record.metrics, {"tests": 2, "failures": 1, "errors": 0, "skipped": 0})
        self.assertAlmostEqual(record.duration, 0.3)
        self.assertEqual(len(record.test_functions), 2)
        self.assertEqual([item["status"] for item in record.test_functions], ["PASS", "FAIL"])

    def test_unittest_result_uses_flat_execution_files(self) -> None:
        root = Path("test_envs/tests/.tmp/ct_framework/unit-flat-result")
        record = ResultRecord(
            "unittest",
            "FAIL",
            "unit",
            0.2,
            execution_id="20260101_010203_123456",
            test_functions=(
                {
                    "path": "test_envs/tests/unittest/python/test_example.py",
                    "function": "ExampleTests::test_failure",
                    "pass": False,
                    "status": "FAIL",
                    "duration": 0.2,
                    "failure": "expected true",
                },
            ),
        )
        path = ResultStore(root).save(record)
        self.assertEqual(
            path,
            root / "results/unittest/20260101_010203_123456_result.json",
        )
        self.assertTrue((path.parent / "20260101_010203_123456_result.log").exists())
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertNotIn("test_case", payload)
        self.assertNotIn("test_id", json.dumps(payload))
        self.assertEqual(payload["summary"]["failed"], 1)
        self.assertFalse(payload["test_functions"][0]["pass"])


if __name__ == "__main__":
    unittest.main()
