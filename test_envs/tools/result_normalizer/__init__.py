from __future__ import annotations

import json
import os
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from test_envs.tools.configuration import configured_now

VALID_STATUSES = {"PASS", "FAIL", "ERROR", "SKIP"}


def _execution_id() -> str:
    return configured_now().strftime("%Y%m%d_%H%M%S_%f")


def _git_value(environment_names: tuple[str, ...], command: list[str], fallback: str) -> str:
    for name in environment_names:
        if value := os.getenv(name):
            return value
    try:
        result = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parents[3],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return result.stdout.strip() or fallback
    except (OSError, subprocess.TimeoutExpired):
        return fallback


def _commit() -> str:
    return _git_value(("GITHUB_SHA", "CI_COMMIT_SHA"), ["git", "rev-parse", "HEAD"], "unknown")


def _branch() -> str:
    return _git_value(
        ("GITHUB_HEAD_REF", "GITHUB_REF_NAME", "CI_COMMIT_REF_NAME"),
        ["git", "branch", "--show-current"],
        "unknown",
    )


@dataclass
class ResultRecord:
    test_id: str
    status: str
    category: str
    duration: float
    description: str = "Automated test execution"
    environment: str = "local"
    configuration: Mapping[str, Any] = field(default_factory=dict)
    test_mode: str = "mock"
    interface: str = "None"
    interface_mode: str = "none"
    equipment: str = "None"
    equipment_mode: str = "none"
    commit: str = field(default_factory=_commit)
    branch: str = field(default_factory=_branch)
    runner: str = "local"
    execution_id: str = field(default_factory=_execution_id)
    timestamp: str = field(default_factory=lambda: configured_now().isoformat())
    metrics: Mapping[str, Any] = field(default_factory=dict)
    statistics: Mapping[str, Any] = field(default_factory=dict)
    logs: Mapping[str, str] = field(default_factory=lambda: {"main": "test.log"})

    def __post_init__(self) -> None:
        self.status = self.status.upper()
        if self.status not in VALID_STATUSES:
            raise ValueError(f"unsupported status: {self.status}")
        if not self.test_id or any(char.isspace() for char in self.test_id):
            raise ValueError("test_id must be a non-empty identifier without spaces")
        if self.duration < 0:
            raise ValueError("duration cannot be negative")
        for name in ("test_mode", "interface_mode", "equipment_mode"):
            value = getattr(self, name)
            if value not in {"mock", "hil", "none"}:
                raise ValueError(f"{name} must be mock, hil, or none: {value}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_case": {
                "test_id": self.test_id,
                "status": self.status,
                "category": self.category,
                "duration": self.duration,
                "description": self.description,
                "environment": self.environment,
            },
            "test_configs": dict(self.configuration),
            "fixture_configs": {
                "test_mode": self.test_mode,
                "interface_mode": self.interface_mode,
                "equipment_mode": self.equipment_mode,
                "interface": self.interface,
                "equipment": self.equipment,
            },
            "test_src": {
                "commit": self.commit,
                "branch": self.branch,
            },
            "test_result": {
                "execution_id": self.execution_id,
                "timestamp": self.timestamp,
                "metrics": dict(self.metrics),
                "statistics": dict(self.statistics),
                "logs": dict(self.logs),
            },
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ResultRecord":
        if "test_case" in value:
            test_case = dict(value["test_case"])
            test_configs = dict(value.get("test_configs", {}))
            fixture_configs = dict(
                value.get("fixture_configs", value.get("fixure_configs", value.get("fixure configs", {})))
            )
            test_src = dict(value.get("test_src", {}))
            test_result = dict(value.get("test_result", {}))
            value = {
                **test_case,
                "configuration": test_configs,
                **fixture_configs,
                **test_src,
                **test_result,
            }
        known = {item.name for item in cls.__dataclass_fields__.values()}
        payload = {key: val for key, val in value.items() if key in known}
        payload.setdefault("commit", "unknown")
        payload.setdefault("branch", "unknown")
        return cls(**payload)


class ResultStore:
    def __init__(self, root: str | Path = "test_envs/reports") -> None:
        self.root = Path(root)

    def save(self, record: ResultRecord) -> Path:
        report_dir = self._report_dir(record)
        report_dir.mkdir(parents=True, exist_ok=True)
        record.logs = {"main": f"{record.execution_id}_test.log"}
        log_path = report_dir / record.logs["main"]
        if not log_path.exists():
            log_path.write_text("", encoding="utf-8")

        payload = record.to_dict()
        result_path = report_dir / f"{record.execution_id}_result.json"
        result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        os.environ["CICT_RESULT_PATH"] = str(result_path)
        return result_path

    def latest(self) -> Path:
        candidates = self.result_paths()
        if not candidates:
            raise FileNotFoundError("No normalized result exists under test_envs/reports")
        return max(candidates, key=lambda path: path.name)

    def result_paths(self, test_id: str | None = None) -> list[Path]:
        name = test_id or "*"
        return list((self.root / "results" / "pytest" / "test_cases").glob(f"{name}/*_result.json")) + list(
            (self.root / "results" / "unittest").glob(f"{name}/*_result.json")
        )

    def _report_dir(self, record: ResultRecord) -> Path:
        if record.category.lower() == "unit":
            return self.root / "results" / "unittest" / record.test_id
        return self.root / "results" / "pytest" / "test_cases" / record.test_id

    def load(self, path: str | Path | None = None) -> ResultRecord:
        source = Path(path) if path else self.latest()
        record = ResultRecord.from_dict(json.loads(source.read_text(encoding="utf-8")))
        expected = f"{record.execution_id}_test.log"
        configured = Path(record.logs.get("main", expected)).name
        record.logs = {"main": configured if (source.parent / configured).exists() else expected}
        return record


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
        environment="github_local_runner" if os.getenv("GITHUB_ACTIONS") == "true" else "local",
        runner=os.getenv("RUNNER_NAME", "local"),
        metrics=totals,
    )


__all__ = ["ResultRecord", "ResultStore", "VALID_STATUSES", "from_junit"]
