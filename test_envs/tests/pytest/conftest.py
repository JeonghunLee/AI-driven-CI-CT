from __future__ import annotations

import os
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import pytest

from test_envs.tools.result_normalizer import ResultRecord, ResultStore


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
    if override in {"mock", "hil"}:
        return override
    marker = request.node.get_closest_marker("ct")
    if marker is None:
        raise RuntimeError("Fixture mode requires @pytest.mark.ct")
    return str(marker.kwargs["fixture_mode"])


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
        if marker.kwargs["fixture_id"] != expected_fixture_id:
            raise pytest.UsageError(
                f"Fixture ID mismatch for {item.nodeid}: "
                f"{marker.kwargs['fixture_id']} != {expected_fixture_id}"
            )
        if marker.kwargs["fixture_mode"] not in {"mock", "hil"}:
            raise pytest.UsageError(f"Invalid fixture_mode for {test_id}: {marker.kwargs['fixture_mode']}")
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
    equipment = values.get("equipment", "None")
    result = ResultRecord(
        test_id=test_id,
        status=status,
        category=values.get("category", "functional"),
        duration=perf_counter() - started,
        description=values.get("description", request.node.name),
        environment=os.getenv("CI", "local"),
        configuration={key: value for key, value in values.items() if key not in {"test_id", "description"}},
        test_mode=test_mode,
        interface=values.get("interface", "None"),
        interface_mode=test_mode,
        equipment=equipment,
        equipment_mode=test_mode if equipment != "None" else "none",
        runner=os.getenv("RUNNER_NAME", "local"),
        metrics=recorder.metrics,
        statistics=recorder.statistics,
    )
    store = ResultStore()
    result_path = store.save(result)
    report_dir = result_path.parent
    detail = str(report.longrepr) if report is not None and report.failed else ""
    (report_dir / result.logs["main"]).write_text(f"status={status}\n{detail}", encoding="utf-8")
    (report_dir / result.logs["stdout"]).write_text(getattr(report, "capstdout", ""), encoding="utf-8")
    (report_dir / result.logs["stderr"]).write_text(getattr(report, "capstderr", ""), encoding="utf-8")
    (report_dir / result.logs["equipment"]).write_text(
        "\n".join(f"{key}={value}" for key, value in recorder.statistics.items()), encoding="utf-8"
    )
    (report_dir / result.logs["interface"]).write_text(
        "\n".join(f"{key}={value}" for key, value in recorder.metrics.items()), encoding="utf-8"
    )
