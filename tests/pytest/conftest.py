from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

import pytest

from tests.pytest.test_equipments.saleae import MockSaleaeController
from tests.pytest.test_equipments.digilent import MockDigilentController
from tests.pytest.test_interfaces.uart import MockUARTInterface
from tests.pytest.test_interfaces.usb import MockUSBInterface
from tests.pytest.test_interfaces.network import MockNetworkInterface
from tools.result_normalizer import ResultRecord, ResultStore

ROOT = Path(__file__).resolve().parents[2]
TEST_CASE_CATALOG = Path(__file__).resolve().parent / "test_cases" / "catalog.json"
EQUIPMENT_CATALOG = Path(__file__).resolve().parent / "test_equipments" / "catalog.json"
INTERFACE_CATALOG = Path(__file__).resolve().parent / "test_interfaces" / "catalog.json"


def load_test_case_catalog() -> dict[str, dict[str, Any]]:
    payload = json.loads(TEST_CASE_CATALOG.read_text(encoding="utf-8"))
    entries = payload.get("test_cases", [])
    if not isinstance(entries, list):
        raise pytest.UsageError("test_cases/catalog.json: test_cases must be a list")
    catalog: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("test_id"), str):
            raise pytest.UsageError("test_cases/catalog.json: invalid test case entry")
        test_id = entry["test_id"]
        if test_id in catalog:
            raise pytest.UsageError(f"test_cases/catalog.json: duplicate test_id: {test_id}")
        catalog[test_id] = entry
    return catalog


def load_tool_catalog(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("tools", [])
    if not isinstance(entries, list):
        raise pytest.UsageError(f"{path.as_posix()}: tools must be a list")
    catalog: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("tool_id"), str):
            raise pytest.UsageError(f"{path.as_posix()}: invalid tool entry")
        tool_id = entry["tool_id"]
        if tool_id in catalog:
            raise pytest.UsageError(f"{path.as_posix()}: duplicate tool_id: {tool_id}")
        catalog[tool_id] = entry
    return catalog


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    catalog = load_test_case_catalog()
    interfaces = load_tool_catalog(INTERFACE_CATALOG)
    equipments = load_tool_catalog(EQUIPMENT_CATALOG)
    for item in items:
        marker = item.get_closest_marker("ct")
        if marker is None:
            continue
        test_id = marker.kwargs.get("test_id")
        if test_id not in catalog:
            raise pytest.UsageError(f"Unregistered CT test_id: {test_id}")
        module = Path(str(item.path)).resolve().relative_to(ROOT).as_posix()
        if module != catalog[test_id].get("module"):
            raise pytest.UsageError(
                f"CT module mismatch for {test_id}: {module} != {catalog[test_id].get('module')}"
            )
        entry = catalog[test_id]
        interface_tool = entry.get("interface_tool")
        equipment_tool = entry.get("equipment_tool")
        if interface_tool not in interfaces:
            raise pytest.UsageError(f"Unknown interface tool for {test_id}: {interface_tool}")
        if equipment_tool is not None and equipment_tool not in equipments:
            raise pytest.UsageError(f"Unknown equipment tool for {test_id}: {equipment_tool}")
        if marker.kwargs.get("interface") != interfaces[interface_tool].get("name"):
            raise pytest.UsageError(f"Interface marker mismatch for {test_id}")
        expected_equipment = equipments[equipment_tool]["name"] if equipment_tool else "None"
        if marker.kwargs.get("equipment", "None") != expected_equipment:
            raise pytest.UsageError(f"Equipment marker mismatch for {test_id}")


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
def usb() -> MockUSBInterface:
    interface = MockUSBInterface()
    interface.connect()
    yield interface
    interface.disconnect()


@pytest.fixture
def network() -> MockNetworkInterface:
    interface = MockNetworkInterface()
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
def digilent(usb: MockUSBInterface) -> MockDigilentController:
    equipment = MockDigilentController(usb)
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
        description=values.get("description", request.node.name),
        environment=os.getenv("CI", "local"),
        configuration={key: value for key, value in values.items() if key not in {"test_id", "description"}},
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
