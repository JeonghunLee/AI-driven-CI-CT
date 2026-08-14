import json
import unittest
from pathlib import Path

from test_envs.tools.result_normalizer import ResultRecord, ResultStore, from_junit


class ResultNormalizerTests(unittest.TestCase):
    def test_result_store_creates_canonical_result_and_logs(self) -> None:
        test_root = Path("test_envs/reports/test-artifacts/unit-result-store")
        record = ResultRecord("UT-NORMALIZER-001", "pass", "functional", 0.1)
        path = ResultStore(test_root).save(record)
        self.assertEqual(json.loads(path.read_text())["status"], "PASS")
        self.assertEqual(ResultStore(test_root).latest(), path)
        self.assertTrue((path.parent / "test.log").exists())
        self.assertTrue(
            (test_root / "measurements" / record.test_id / record.execution_id / "measurement.csv").exists()
        )

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
            test_mode="hil",
            interface="JTAG",
            interface_mode="hil",
            equipment="FPGA",
            equipment_mode="hil",
        )
        self.assertEqual(result.to_dict()["test_mode"], "hil")
        self.assertEqual(result.to_dict()["interface_mode"], "hil")
        self.assertEqual(result.to_dict()["equipment_mode"], "hil")

    def test_junit_normalization(self) -> None:
        record = from_junit("test_envs/tests/fixtures/junit.xml", "UNIT-SAMPLE")
        self.assertEqual(record.status, "FAIL")
        self.assertEqual(record.metrics, {"tests": 2, "failures": 1, "errors": 0, "skipped": 0})
        self.assertAlmostEqual(record.duration, 0.3)


if __name__ == "__main__":
    unittest.main()
