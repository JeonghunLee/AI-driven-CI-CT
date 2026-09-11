from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from test_envs.tools.configuration import configured_now


ROOT = Path(__file__).resolve().parents[3]
TEST_CASE_ROOT = ROOT / "test_envs" / "tests" / "pytest" / "test_cases"
CATALOG_PATH = TEST_CASE_ROOT / "test_catalog.json"
TASKS_PATH = ROOT / ".vscode" / "tasks.json"
PYTEST_ISSUE_TEMPLATE_PATH = ROOT / ".github" / "ISSUE_TEMPLATE" / "pytest_request.yml"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "continuous-test.yml"
REQUIRED_FIELDS = ("test_id", "category", "fixture_id", "fixture_mode")
FIXTURE_MODES = {"mock", "hil"}


def _ct_markers(source_path: Path) -> list[dict[str, Any]]:
    source_path = source_path.resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    markers: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            marker_owner = decorator.func.value
            if (
                decorator.func.attr != "ct"
                or not isinstance(marker_owner, ast.Attribute)
                or marker_owner.attr != "mark"
                or not isinstance(marker_owner.value, ast.Name)
                or marker_owner.value.id != "pytest"
            ):
                continue
            values: dict[str, Any] = {}
            for keyword in decorator.keywords:
                if keyword.arg is None:
                    raise ValueError(f"CT marker **kwargs are not supported: {source_path}:{node.lineno}")
                try:
                    values[keyword.arg] = ast.literal_eval(keyword.value)
                except (ValueError, TypeError) as error:
                    raise ValueError(
                        f"CT marker values must be literals: {source_path}:{node.lineno}:{keyword.arg}"
                    ) from error
            missing = [field for field in REQUIRED_FIELDS if field not in values]
            if missing:
                raise ValueError(f"Missing CT marker fields {missing}: {source_path}:{node.lineno}")
            marker = {
                "test_id": values["test_id"],
                "category": values["category"],
                "fixture_id": values["fixture_id"],
                "default_fixture_mode": values["fixture_mode"],
                "test_prompt": values.get("test_prompt", ""),
                "test_path": source_path.relative_to(ROOT).as_posix(),
            }
            for field in ("test_id", "category", "fixture_id", "default_fixture_mode", "test_prompt"):
                if not isinstance(marker[field], str):
                    raise ValueError(f"CT marker {field} must be a string: {source_path}:{node.lineno}")
            for field in ("test_id", "category", "fixture_id"):
                if not marker[field]:
                    raise ValueError(f"CT marker {field} must not be empty: {source_path}:{node.lineno}")
            if marker["default_fixture_mode"] not in FIXTURE_MODES:
                raise ValueError(
                    f"Invalid default fixture mode {marker['default_fixture_mode']!r}: {source_path}:{node.lineno}"
                )
            markers.append(marker)
    return markers


def discover_tests(test_case_root: Path = TEST_CASE_ROOT) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []
    for source_path in sorted(test_case_root.glob("*.py")):
        if source_path.name == "__init__.py":
            continue
        tests.extend(_ct_markers(source_path))
    seen: dict[str, str] = {}
    for test in tests:
        test_id = test["test_id"]
        if not test_id:
            raise ValueError(f"Empty TEST ID: {test['test_path']}")
        if test_id in seen:
            raise ValueError(f"Duplicate TEST ID {test_id}: {seen[test_id]} and {test['test_path']}")
        seen[test_id] = test["test_path"]
    return tests


def _replace(pattern: str, replacement: str, text: str, path: Path) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"Cannot synchronize TEST IDs in {path}")
    return updated


def _sync_tasks(test_ids: list[str]) -> None:
    text = TASKS_PATH.read_text(encoding="utf-8")
    options = "[\n" + ",\n".join(f'                "{test_id}"' for test_id in test_ids) + "\n            ]"
    replacement = rf'\g<1>{options}\g<2>"{test_ids[0]}"'
    text = _replace(
        r'("id"\s*:\s*"testCaseId".*?"options"\s*:\s*)\[.*?\](\s*,\s*"default"\s*:\s*)"[^"]*"',
        replacement,
        text,
        TASKS_PATH,
    )
    TASKS_PATH.write_text(text, encoding="utf-8")


def _sync_issue_template(test_ids: list[str]) -> None:
    text = PYTEST_ISSUE_TEMPLATE_PATH.read_text(encoding="utf-8")
    options = "      options:\n" + "".join(f"        - {test_id}\n" for test_id in test_ids)
    text = _replace(
        r"(    id: test_id\n.*?)(      options:\n(?:        - .*\n)+)(      default: 0\n.*?)(?=  - type: dropdown\n    id: fixture_mode)",
        rf"\g<1>{options}\g<3>",
        text,
        PYTEST_ISSUE_TEMPLATE_PATH,
    )
    PYTEST_ISSUE_TEMPLATE_PATH.write_text(text, encoding="utf-8")


def _sync_workflow(test_ids: list[str]) -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    inline = ", ".join(test_ids)
    text = _replace(
        r"(      test_id:\n.*?        options: )\[[^\n]*\](\n        default: )[^\n]+(?=\n      fixture_mode:)",
        rf"\g<1>[{inline}]\g<2>{test_ids[0]}",
        text,
        WORKFLOW_PATH,
    )
    WORKFLOW_PATH.write_text(text, encoding="utf-8")


def synchronize_consumers(tests: list[dict[str, Any]]) -> None:
    test_ids = [test["test_id"] for test in tests]
    if not test_ids:
        raise ValueError("No Pytest CT markers were discovered")
    _sync_tasks(test_ids)
    _sync_issue_template(test_ids)
    _sync_workflow(test_ids)


def generate_catalog(*, sync_consumers: bool = True) -> dict[str, Any]:
    tests = discover_tests()
    catalog = {
        "version": 1,
        "generated_date": configured_now().isoformat(timespec="seconds"),
        "tests": tests,
    }
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if sync_consumers:
        synchronize_consumers(tests)
    return catalog


def load_catalog(*, refresh_if_stale: bool = True) -> dict[str, Any]:
    sources = [path for path in TEST_CASE_ROOT.glob("*.py") if path.name != "__init__.py"]
    stale = not CATALOG_PATH.is_file() or any(
        path.stat().st_mtime_ns > CATALOG_PATH.stat().st_mtime_ns for path in sources
    )
    if refresh_if_stale and stale:
        return generate_catalog(sync_consumers=False)
    value = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if value.get("version") != 1 or not isinstance(value.get("tests"), list):
        raise ValueError(f"Invalid Pytest test catalog: {CATALOG_PATH}")
    return value


def catalog_tests() -> list[dict[str, Any]]:
    return list(load_catalog()["tests"])


def catalog_by_id() -> dict[str, dict[str, Any]]:
    return {test["test_id"]: test for test in catalog_tests()}


__all__ = [
    "CATALOG_PATH",
    "catalog_by_id",
    "catalog_tests",
    "discover_tests",
    "generate_catalog",
    "load_catalog",
    "synchronize_consumers",
]
