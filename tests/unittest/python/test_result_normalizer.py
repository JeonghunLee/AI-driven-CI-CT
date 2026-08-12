import json
from pathlib import Path

import pytest

from tools.result_normalizer import ResultRecord, ResultStore, from_junit


def test_result_store_creates_canonical_result_and_logs() -> None:
    test_root = Path("reports/raw/unit-result-store")
    record = ResultRecord("UT-NORMALIZER-001", "pass", "functional", 0.1)
    path = ResultStore(test_root).save(record)
    assert json.loads(path.read_text())["status"] == "PASS"
    assert (test_root / "json" / "latest.json").exists()
    assert (path.parent / "test.log").exists()


def test_result_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        ResultRecord("UT-001", "maybe", "functional", 0.0)


def test_junit_normalization() -> None:
    record = from_junit("tests/fixtures/junit.xml", "UNIT-SAMPLE")
    assert record.status == "FAIL"
    assert record.metrics == {"tests": 2, "failures": 1, "errors": 0, "skipped": 0}
    assert record.duration == pytest.approx(0.3)
