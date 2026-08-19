from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pytest

from test_envs.tools.result_normalizer import ResultRecord, ResultStore


@dataclass
class FunctionResult:
    function: str
    status: str
    duration: float
    failure: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "function": self.function,
            "pass": self.status == "PASS",
            "status": self.status,
            "duration": self.duration,
            "failure": self.failure,
        }


_FUNCTION_RESULTS: dict[str, FunctionResult] = {}


def _function_name(nodeid: str) -> str:
    parts = nodeid.split("::")
    return "::".join(parts[1:]) if len(parts) > 1 else parts[0]


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if not report.nodeid.replace("\\", "/").startswith("test_envs/tests/unittest/"):
        return
    function = _function_name(report.nodeid)
    current = _FUNCTION_RESULTS.get(report.nodeid)
    if report.when == "setup" and report.failed:
        _FUNCTION_RESULTS[report.nodeid] = FunctionResult(
            function=function,
            status="ERROR",
            duration=report.duration,
            failure=str(report.longrepr),
        )
    elif report.when == "call":
        status = "PASS" if report.passed else "SKIP" if report.skipped else "FAIL"
        _FUNCTION_RESULTS[report.nodeid] = FunctionResult(
            function=function,
            status=status,
            duration=report.duration,
            failure=str(report.longrepr) if report.failed else "",
        )
    elif report.when == "teardown" and report.failed:
        duration = report.duration + (current.duration if current else 0.0)
        _FUNCTION_RESULTS[report.nodeid] = FunctionResult(
            function=function,
            status="ERROR",
            duration=duration,
            failure=str(report.longrepr),
        )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if not _FUNCTION_RESULTS:
        return
    functions = tuple(item.to_dict() for _, item in sorted(_FUNCTION_RESULTS.items()))
    statuses = {item["status"] for item in functions}
    status = "ERROR" if "ERROR" in statuses else "FAIL" if "FAIL" in statuses else "PASS"
    record = ResultRecord(
        test_id="unittest",
        status=status,
        category="unit",
        duration=sum(float(item["duration"]) for item in functions),
        description="unittest execution",
        environment="github_local_runner" if os.getenv("GITHUB_ACTIONS") == "true" else "local",
        runner=os.getenv("RUNNER_NAME", "local"),
        test_functions=functions,
    )
    store = ResultStore()
    result_path = store.save(record)
    summary = record.to_dict()["summary"]
    lines = [
        "[execution]",
        f"execution_id={record.execution_id}",
        f"timestamp={record.timestamp}",
        f"status={record.status}",
        f"total={summary['total']}",
        f"passed={summary['passed']}",
        f"failed={summary['failed']}",
        f"errors={summary['errors']}",
        f"skipped={summary['skipped']}",
        "",
        "[test_functions]",
    ]
    for item in functions:
        lines.append(
            f"{item['status']} | {item['function']} | duration={float(item['duration']):.6f}s"
        )
    failed = [item for item in functions if item["status"] in {"FAIL", "ERROR"}]
    if failed:
        lines.extend(["", "[failed_functions]"])
        for item in failed:
            lines.extend([f"{item['function']} | {item['status']}", str(item["failure"]), ""])
    (result_path.parent / record.logs["main"]).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    session.config._unittest_result_path = result_path
