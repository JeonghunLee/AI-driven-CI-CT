from __future__ import annotations

import os
import importlib
import pkgutil
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

import pytest

from test_envs.tools.result_normalizer import ResultRecord, ResultStore


@lru_cache(maxsize=1)
def fixture_registry() -> dict[str, Mapping[str, Any]]:
    package_name = "test_envs.tests.pytest.fixtures"
    fixtures_path = Path(__file__).parent / "fixtures"
    registry: dict[str, Mapping[str, Any]] = {}
    for module_info in pkgutil.iter_modules([str(fixtures_path)]):
        if not module_info.name.startswith("fixture_"):
            continue
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        meta = getattr(module, "FIXTURE_META", None)
        if not isinstance(meta, dict):
            raise ValueError(f"{module_info.name}: FIXTURE_META is required")
        fixture_id = meta.get("fixture_id")
        interfaces = meta.get("interfaces")
        equipments = meta.get("equipments")
        modes = meta.get("modes")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise ValueError(f"{module_info.name}: invalid fixture_id")
        if fixture_id in registry:
            raise ValueError(f"duplicate fixture_id: {fixture_id}")
        if not isinstance(interfaces, list) or not all(isinstance(value, str) for value in interfaces):
            raise ValueError(f"{fixture_id}: interfaces must be list[str]")
        if not isinstance(equipments, list) or not all(isinstance(value, str) for value in equipments):
            raise ValueError(f"{fixture_id}: equipments must be list[str]")
        if not isinstance(modes, dict):
            raise ValueError(f"{fixture_id}: modes must be a mapping")
        for mode in ("mock", "hil"):
            settings = modes.get(mode)
            if not isinstance(settings, dict) or not isinstance(settings.get("enabled"), bool):
                raise ValueError(f"{fixture_id}: modes.{mode}.enabled must be bool")
        registry[fixture_id] = meta
    return registry


def fixture_meta(fixture_id: str) -> Mapping[str, Any]:
    try:
        return fixture_registry()[fixture_id]
    except KeyError as error:
        raise ValueError(f"unknown fixture_id: {fixture_id}") from error


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--test-id", action="store", help="Run one CT TEST ID")
    parser.addoption(
        "--fixture-mode",
        action="store",
        choices=("marker", "mock", "hil"),
        default="marker",
        help="Override @pytest.mark.ct fixture_mode; marker uses the marker value",
    )


def effective_fixture_mode(request: pytest.FixtureRequest) -> str:
    override = request.config.getoption("--fixture-mode")
    marker = request.node.get_closest_marker("ct")
    if marker is None:
        raise RuntimeError("Fixture mode requires @pytest.mark.ct")
    mode = str(override if override in {"mock", "hil"} else marker.kwargs["fixture_mode"])
    fixture_id = str(marker.kwargs["fixture_id"])
    try:
        enabled = fixture_meta(fixture_id)["modes"][mode]["enabled"]
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError(f"Invalid fixture metadata for {fixture_id}: {error}") from error
    if not enabled:
        raise RuntimeError(f"{fixture_id} does not enable {mode} mode")
    return mode


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    ct_items: dict[str, pytest.Item] = {}
    required = {"test_id", "category", "fixture_id", "fixture_mode"}
    for item in items:
        marker = item.get_closest_marker("ct")
        if marker is None:
            continue
        missing = sorted(required - marker.kwargs.keys())
        if missing:
            raise pytest.UsageError(f"CT marker missing fields for {item.nodeid}: {', '.join(missing)}")
        test_id = marker.kwargs["test_id"]
        if not isinstance(test_id, str) or not test_id:
            raise pytest.UsageError(f"Invalid CT test_id for {item.nodeid}: {test_id!r}")
        if test_id in ct_items:
            raise pytest.UsageError(f"Duplicate CT test_id: {test_id}")
        name_parts = item.path.stem.split("_", 3)
        expected_fixture_id = (
            f"FIXTURE-{name_parts[2]}"
            if len(name_parts) == 4 and name_parts[:2] == ["test", "fixture"]
            else None
        )
        fixture_id = marker.kwargs["fixture_id"]
        if fixture_id != expected_fixture_id:
            raise pytest.UsageError(
                f"Fixture ID mismatch for {item.nodeid}: "
                f"{marker.kwargs['fixture_id']} != {expected_fixture_id}"
            )
        expected_fixture_name = f"fixture_{name_parts[2]}" if expected_fixture_id else None
        if expected_fixture_name not in item.fixturenames:
            raise pytest.UsageError(
                f"Fixture import mismatch for {item.nodeid}: {expected_fixture_name} is required"
            )
        if marker.kwargs["fixture_mode"] not in {"mock", "hil"}:
            raise pytest.UsageError(f"Invalid fixture_mode for {test_id}: {marker.kwargs['fixture_mode']}")
        try:
            meta = fixture_meta(str(fixture_id))
        except ValueError as error:
            raise pytest.UsageError(str(error)) from error
        if not meta["modes"][marker.kwargs["fixture_mode"]]["enabled"]:
            raise pytest.UsageError(
                f"{fixture_id} does not enable {marker.kwargs['fixture_mode']} mode"
            )
        ct_items[test_id] = item

    selected_test_id = config.getoption("--test-id", default=None)
    if selected_test_id:
        if selected_test_id not in ct_items:
            raise pytest.UsageError(f"Unknown TEST ID: {selected_test_id}")
        selected = [ct_items[selected_test_id]]
        deselected = [item for item in items if item not in selected]
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@dataclass
class CTResultRecorder:
    metrics: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


@pytest.fixture
def ct_result(request: pytest.FixtureRequest) -> CTResultRecorder:
    marker = request.node.get_closest_marker("ct")
    if marker is None:
        raise RuntimeError("ct_result can only be used by a test marked with @pytest.mark.ct")
    test_id = marker.kwargs.get("test_id", request.node.name.upper())
    recorder = CTResultRecorder()
    started = perf_counter()
    yield recorder
    report = getattr(request.node, "rep_call", None)
    status = "PASS" if report is not None and report.passed else "FAIL"
    if report is not None and report.skipped:
        status = "SKIP"
    values = marker.kwargs
    test_mode = effective_fixture_mode(request)
    meta = fixture_meta(str(values["fixture_id"]))
    interfaces = tuple(meta["interfaces"])
    equipments = tuple(meta["equipments"])
    result = ResultRecord(
        test_id=test_id,
        status=status,
        category=values.get("category", "functional"),
        duration=perf_counter() - started,
        description=values.get("description", request.node.name),
        environment="github_local_runner" if os.getenv("GITHUB_ACTIONS") == "true" else "local",
        configuration={key: value for key, value in values.items() if key not in {"test_id", "description"}},
        fixture_id=str(meta["fixture_id"]),
        test_mode=test_mode,
        interfaces=interfaces,
        interface_mode=test_mode,
        equipments=equipments,
        equipment_mode=test_mode if equipments else "none",
        modes=meta["modes"],
        runner=os.getenv("RUNNER_NAME", "local"),
        metrics=recorder.metrics,
        statistics=recorder.statistics,
    )
    store = ResultStore()
    result_path = store.save(result)
    report_dir = result_path.parent
    detail = str(report.longrepr) if report is not None and report.failed else ""
    sections = {
        "TEST": f"timestamp={result.timestamp}\nstatus={status}\n{detail}".rstrip(),
        "STDOUT": getattr(report, "capstdout", ""),
        "STDERR": getattr(report, "capstderr", ""),
        "EQUIPMENT": "\n".join(f"{key}={value}" for key, value in recorder.statistics.items()),
        "INTERFACE": "\n".join(f"{key}={value}" for key, value in recorder.metrics.items()),
    }
    combined = "\n\n".join(f"[{name}]\n{content}" for name, content in sections.items()) + "\n"
    (report_dir / result.logs["main"]).write_text(combined, encoding="utf-8")
