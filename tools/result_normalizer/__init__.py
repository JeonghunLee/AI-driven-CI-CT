from __future__ import annotations

import json
import os
import csv
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

VALID_STATUSES = {"PASS", "FAIL", "ERROR", "SKIP"}


def _execution_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")


@dataclass
class ResultRecord:
    test_id: str
    status: str
    category: str
    duration: float
    description: str = "Automated test execution"
    environment: str = "local"
    configuration: Mapping[str, Any] = field(default_factory=dict)
    interface: str = "None"
    equipment: str = "None"
    commit: str = "local"
    runner: str = "local"
    execution_id: str = field(default_factory=_execution_id)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metrics: Mapping[str, Any] = field(default_factory=dict)
    statistics: Mapping[str, Any] = field(default_factory=dict)
    logs: Mapping[str, str] = field(
        default_factory=lambda: {
            "main": "test.log",
            "stdout": "stdout.log",
            "stderr": "stderr.log",
            "equipment": "equipment.log",
            "interface": "interface.log",
        }
    )

    def __post_init__(self) -> None:
        self.status = self.status.upper()
        if self.status not in VALID_STATUSES:
            raise ValueError(f"unsupported status: {self.status}")
        if not self.test_id or any(char.isspace() for char in self.test_id):
            raise ValueError("test_id must be a non-empty identifier without spaces")
        if self.duration < 0:
            raise ValueError("duration cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ResultRecord":
        known = {item.name for item in cls.__dataclass_fields__.values()}
        return cls(**{key: val for key, val in value.items() if key in known})


class ResultStore:
    def __init__(self, root: str | Path = "reports") -> None:
        self.root = Path(root)

    def save(self, record: ResultRecord) -> Path:
        log_dir = self.root / "logs" / record.test_id / record.execution_id
        log_dir.mkdir(parents=True, exist_ok=True)
        for filename in record.logs.values():
            path = log_dir / filename
            if not path.exists():
                path.write_text("", encoding="utf-8")

        payload = record.to_dict()
        result_path = log_dir / "result.json"
        result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        measurement_dir = self.root / "measurements" / record.test_id / record.execution_id
        measurement_dir.mkdir(parents=True, exist_ok=True)
        (measurement_dir / "measurement.json").write_text(
            json.dumps({"metrics": payload["metrics"], "statistics": payload["statistics"]}, indent=2),
            encoding="utf-8",
        )
        with (measurement_dir / "measurement.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["type", "name", "value"])
            writer.writerows(("metric", key, value) for key, value in record.metrics.items())
            writer.writerows(("statistic", key, value) for key, value in record.statistics.items())
        os.environ["CICT_RESULT_PATH"] = str(result_path)
        return result_path

    def latest(self) -> Path:
        candidates = list((self.root / "logs").glob("*/*/result.json"))
        if not candidates:
            raise FileNotFoundError("No normalized result exists under reports/logs")
        return max(candidates, key=lambda path: path.parent.name)

    def load(self, path: str | Path | None = None) -> ResultRecord:
        source = Path(path) if path else self.latest()
        return ResultRecord.from_dict(json.loads(source.read_text(encoding="utf-8")))


def from_junit(path: str | Path, test_id: str = "UNIT-TEST") -> ResultRecord:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    totals = {
        key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    duration = sum(float(suite.attrib.get("time", 0.0)) for suite in suites)
    status = "FAIL" if totals["failures"] or totals["errors"] else "PASS"
    return ResultRecord(
        test_id=test_id,
        status=status,
        category="unit",
        duration=duration,
        description="Unit test suite",
        environment=os.getenv("CI", "local"),
        commit=os.getenv("GITHUB_SHA", "local")[:7],
        runner=os.getenv("RUNNER_NAME", "local"),
        metrics=totals,
    )


__all__ = ["ResultRecord", "ResultStore", "VALID_STATUSES", "from_junit"]
