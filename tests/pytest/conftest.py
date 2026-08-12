from __future__ import annotations

import os
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import pytest

from tests.pytest.test_equipments.saleae import MockSaleaeController
from tests.pytest.test_interfaces.uart import MockUARTInterface
from tools.result_normalizer import ResultRecord, ResultStore


@dataclass
class CTResultRecorder:
    metrics: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


@pytest.fixture
def uart() -> MockUARTInterface:
    interface = MockUARTInterface()
    interface.connect()
    yield interface
    interface.disconnect()


@pytest.fixture
def saleae(uart: MockUARTInterface) -> MockSaleaeController:
    equipment = MockSaleaeController(uart)
    equipment.connect()
    yield equipment
    equipment.disconnect()


@pytest.fixture
def ct_result(request: pytest.FixtureRequest) -> CTResultRecorder:
    marker = request.node.get_closest_marker("ct")
    if marker is None:
        raise RuntimeError("ct_result can only be used by a test marked with @pytest.mark.ct")
    recorder = CTResultRecorder()
    started = perf_counter()
    yield recorder
    report = getattr(request.node, "rep_call", None)
    status = "PASS" if report is not None and report.passed else "FAIL"
    if report is not None and report.skipped:
        status = "SKIP"
    values = marker.kwargs
    result_path = ResultStore().save(ResultRecord(
        test_id=values.get("test_id", request.node.name.upper()),
        status=status,
        category=values.get("category", "functional"),
        duration=perf_counter() - started,
        interface=values.get("interface", "None"),
        equipment=values.get("equipment", "None"),
        commit=os.getenv("GITHUB_SHA", "local")[:7],
        runner=os.getenv("RUNNER_NAME", "local"),
        metrics=recorder.metrics,
        statistics=recorder.statistics,
    ))
    execution_dir = result_path.parent
    detail = str(report.longrepr) if report is not None and report.failed else ""
    (execution_dir / "test.log").write_text(f"status={status}\n{detail}", encoding="utf-8")
    (execution_dir / "stdout.log").write_text(getattr(report, "capstdout", ""), encoding="utf-8")
    (execution_dir / "stderr.log").write_text(getattr(report, "capstderr", ""), encoding="utf-8")
    (execution_dir / "equipment.log").write_text(
        "\n".join(f"{key}={value}" for key, value in recorder.statistics.items()), encoding="utf-8"
    )
    (execution_dir / "interface.log").write_text(
        "\n".join(f"{key}={value}" for key, value in recorder.metrics.items()), encoding="utf-8"
    )
