from __future__ import annotations

import os
import subprocess
import sys
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from test_envs.test_pipeline.pipeline import run as run_pipeline
from test_envs.tools.configuration import build_check
from test_envs.tools.pandoc_reporter import REFERENCE_DOC, convert, pandoc_executable
from test_envs.tools.result_normalizer import ResultStore
from test_envs.tools.test_catalog import catalog_by_id, catalog_tests


TestType = Literal["pytest", "unittest"]
FixtureMode = Literal["marker", "mock", "hil"]
UnittestScope = Literal["all", "ct_framework_python", "python", "c_cpp", "firmware", "common"]
CoverageMode = Literal["none", "terminal", "html"]
PandocFormat = Literal["none", "docx", "html", "both"]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OLLAMA_TEST_PLAN_PATH = ROOT / "test_envs" / "configs" / "test_ollama.yaml"
UNITTEST_SCOPES = {
    "all": "test_envs/tests/unittest",
    "ct_framework_python": "test_envs/tests/unittest/ct_framework/python",
    "python": "test_envs/tests/unittest/python",
    "c_cpp": "test_envs/tests/unittest/c_cpp",
    "firmware": "test_envs/tests/unittest/firmware",
    "common": "test_envs/tests/unittest/common",
}
_RUN_LOCK = threading.Lock()


@dataclass(frozen=True)
class TestRequest:
    test_type: TestType
    test_id: str = ""
    fixture_mode: FixtureMode = "marker"
    unittest_scope: UnittestScope = "all"
    coverage: CoverageMode = "none"
    markdown: bool = True
    pandoc: PandocFormat = "none"


def pytest_test_list() -> dict[str, object]:
    return {
        "test_ids": [
            {
                "test_id": item["test_id"],
                "path": item["test_path"],
                "category": item["category"],
                "fixture_id": item["fixture_id"],
                "marker_mode": item["default_fixture_mode"],
                "test_prompt": item["test_prompt"],
            }
            for item in catalog_tests()
        ],
        "fixture_modes": ["marker", "mock", "hil"],
        "pytest_hil_allow": _enabled("PYTEST_HIL_ALLOW"),
    }


def unittest_test_list() -> dict[str, object]:
    scopes: list[dict[str, object]] = []
    for name, relative in UNITTEST_SCOPES.items():
        root = ROOT / relative
        scopes.append(
            {
                "scope": name,
                "path": relative,
                "tests": [str(path.relative_to(ROOT)) for path in sorted(root.rglob("test_*.py"))],
            }
        )
    return {"scopes": scopes}


def all_test_lists() -> dict[str, object]:
    return {
        "pytest": pytest_test_list(),
        "unittest": unittest_test_list(),
        "coverage_modes": ["none", "terminal", "html"],
        "pandoc_formats": ["none", "docx", "html", "both"],
    }


def ollama_test_plan() -> dict[str, Any]:
    """Load and validate the Ollama MCP test plan without executing it."""
    path = ollama_test_plan_path()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise RuntimeError(f"Invalid Ollama test plan: {path}: {error}") from error
    if not isinstance(raw, dict):
        raise RuntimeError("Invalid Ollama test plan: root must be a mapping")
    return _validate_ollama_test_plan(raw)


def ollama_test_plan_path() -> Path:
    configured = os.getenv("OLLAMA_TEST_PLAN", "").strip()
    if not configured:
        return DEFAULT_OLLAMA_TEST_PLAN_PATH
    path = Path(configured)
    return path if path.is_absolute() else ROOT / path


def run_ollama_test_plan() -> dict[str, object]:
    """Execute the allowlisted test and report workflow defined in test_ollama.yaml."""
    plan = ollama_test_plan()
    ollama = build_check().get("ollama", {})
    if not isinstance(ollama, dict) or not ollama.get("available") or not ollama.get("selected_model_installed"):
        raise RuntimeError("Ollama must be available with the selected model before running test_ollama.yaml")
    if plan["agent"]["model"] != ollama.get("selected_model"):
        raise RuntimeError("test_ollama.yaml agent.model must match config_ollama.json selected_model")

    selection = plan["selection"]
    reports = plan["reports"]
    execution = plan["execution"]
    pytest_plan = selection["pytest"]
    unittest_plan = selection["unittest"]
    pytest_ids = list(catalog_by_id()) if pytest_plan["mode"] == "all" else pytest_plan["test_ids"]
    unittest_scopes = ["all"] if unittest_plan["mode"] == "all" else unittest_plan["scopes"]
    results: dict[str, list[dict[str, object]]] = {"pytest": [], "unittest": []}

    for test_id in pytest_ids:
        results["pytest"].append(
            run_test(
                TestRequest(
                    test_type="pytest",
                    test_id=test_id,
                    fixture_mode=pytest_plan["fixture_mode"],
                    coverage=execution["coverage"],
                    markdown=reports["markdown"],
                    pandoc=reports["pandoc"],
                ),
                execution["timeout_seconds"],
            )
        )
    for scope in unittest_scopes:
        results["unittest"].append(
            run_test(
                TestRequest(
                    test_type="unittest",
                    unittest_scope=scope,
                    coverage=execution["coverage"],
                    markdown=reports["markdown"],
                    pandoc=reports["pandoc"],
                ),
                execution["timeout_seconds"],
            )
        )
    return {
        "plan_path": _relative(ollama_test_plan_path()),
        "ollama_model": ollama.get("selected_model"),
        "selection": selection,
        "results": results,
    }


def test_environment() -> dict[str, object]:
    check = build_check()
    venv_python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    check["venv"] = {
        "available": venv_python.is_file(),
        "python": str(venv_python),
        "active": Path(sys.executable).resolve() == venv_python.resolve(),
    }
    executable = pandoc_executable()
    check["pandoc"] = {
        "installed": executable is not None,
        "executable": executable,
        "reference_docx": str(ROOT / REFERENCE_DOC),
        "reference_docx_available": (ROOT / REFERENCE_DOC).is_file(),
    }
    check["mcp"] = {
        "transport": "stdio",
        "pytest_hil_allow": _enabled("PYTEST_HIL_ALLOW"),
        "mkdoc_update": _enabled("MKDOC_UPDATE"),
        "ollama_test_plan": _relative(ollama_test_plan_path()),
    }
    return check


def run_test(
    request: TestRequest,
    timeout_seconds: int = 3600,
    environment: dict[str, str] | None = None,
) -> dict[str, object]:
    _validate(request, timeout_seconds)
    with _RUN_LOCK:
        store = ResultStore(ROOT / "test_reports")
        before = {path.resolve() for path in store.result_paths()}
        command = _pytest_command(request)
        process_environment = {
            **os.environ,
            "TEST_REQUEST": os.getenv("TEST_REQUEST", "mcp"),
            "TEST_NAME": os.getenv("TEST_NAME", os.getenv("RUNNER_NAME", "local_01")),
        }
        process_environment.update(environment or {})
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=process_environment,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        created = [path for path in store.result_paths() if path.resolve() not in before]
        result_path = max(created, key=lambda path: path.stat().st_mtime_ns) if created else None
        response: dict[str, object] = {
            "request": asdict(request),
            "command": command,
            "exit_code": completed.returncode,
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-8000:],
            "result_path": _relative(result_path) if result_path else None,
            "reports": {},
        }
        if result_path is None:
            response["status"] = "ERROR"
            response["error"] = "The test process did not create a normalized result."
            return response

        record = store.load(result_path)
        response["status"] = record.status
        response["execution_id"] = record.execution_id
        reports: dict[str, str] = {"log": _relative(result_path.parent / record.logs["main"])}
        if request.markdown or request.pandoc != "none":
            pipeline_result = run_pipeline(result_path=result_path)
            markdown_path = Path(str(pipeline_result["markdown"]))
            reports["markdown"] = _relative(markdown_path)
            reports.update(_convert_pandoc(markdown_path, request.pandoc))
        response["reports"] = reports
        return response


def run_all_tests(
    test_id: str = "",
    fixture_mode: FixtureMode = "marker",
    unittest_scope: UnittestScope = "all",
    coverage: CoverageMode = "none",
    markdown: bool = True,
    pandoc: PandocFormat = "none",
    timeout_seconds: int = 3600,
) -> dict[str, object]:
    test_id = test_id or _default_test_id()
    pytest_result = run_test(
        TestRequest("pytest", test_id, fixture_mode, coverage=coverage, markdown=markdown, pandoc=pandoc),
        timeout_seconds,
    )
    unittest_result = run_test(
        TestRequest(
            "unittest",
            unittest_scope=unittest_scope,
            coverage=coverage,
            markdown=markdown,
            pandoc=pandoc,
        ),
        timeout_seconds,
    )
    return {"pytest": pytest_result, "unittest": unittest_result}


def update_latest(
    test_type: TestType,
    test_id: str = "",
    markdown: bool = True,
    pandoc: PandocFormat = "none",
) -> dict[str, object]:
    store, path = _latest_path(test_type, test_id)
    record = store.load(path)
    log_path = path.parent / record.logs["main"]
    reports: dict[str, str] = {"log": _relative(log_path)}
    if markdown or pandoc != "none":
        pipeline_result = run_pipeline(result_path=path)
        markdown_path = Path(str(pipeline_result["markdown"]))
        reports["markdown"] = _relative(markdown_path)
        reports.update(_convert_pandoc(markdown_path, pandoc))
    return {
        "path": _relative(path),
        "result": record.to_dict(),
        "log": log_path.read_text(encoding="utf-8", errors="replace")[-8000:],
        "reports": reports,
    }


def update_mkdocs(test_type: TestType, test_id: str = "") -> dict[str, object]:
    if not _enabled("MKDOC_UPDATE"):
        raise PermissionError("MkDocs update requires MKDOC_UPDATE=true")
    store, path = _latest_path(test_type, test_id)
    record = store.load(path)
    pipeline_result = run_pipeline(publish_docs=True, result_path=path)
    published = (
        ROOT / "docs" / "tests" / "unittest" / f"{record.execution_id}.md"
        if test_type == "unittest"
        else ROOT / "docs" / "tests" / "pytest" / f"{record.test_id}__{record.execution_id}.md"
    )
    return {
        "result_path": _relative(path),
        "markdown": _relative(Path(str(pipeline_result["markdown"]))),
        "mkdocs": _relative(published),
        "updated": published.is_file(),
    }


def latest_result(test_type: TestType, test_id: str = "") -> dict[str, object]:
    store, path = _latest_path(test_type, test_id)
    return {"path": _relative(path), "result": store.load(path).to_dict()}


def _latest_path(test_type: TestType, test_id: str) -> tuple[ResultStore, Path]:
    if test_type not in {"pytest", "unittest"}:
        raise ValueError("test_type must be pytest or unittest")
    test_ids = catalog_by_id()
    if test_type == "pytest" and test_id not in test_ids:
        raise ValueError(f"test_id must be one of: {', '.join(test_ids)}")
    if test_type == "unittest" and test_id:
        raise ValueError("test_id does not apply to unittest")
    store = ResultStore(ROOT / "test_reports")
    paths = store.result_paths(test_id if test_type == "pytest" else "unittest")
    if not paths:
        raise FileNotFoundError("No matching normalized test result exists")
    return store, max(paths, key=lambda item: item.stat().st_mtime_ns)


def _pytest_command(request: TestRequest) -> list[str]:
    command = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"]
    if request.test_type == "pytest":
        command.extend(
            [
                "test_envs/tests/pytest/test_cases",
                "--test-id",
                request.test_id,
                "--fixture-mode",
                request.fixture_mode,
                "-m",
                "ct",
                "-s",
            ]
        )
    else:
        command.extend([UNITTEST_SCOPES[request.unittest_scope], "-s"])
    if request.coverage == "terminal":
        command.extend(["--cov=test_envs", "--cov-report=term-missing"])
    elif request.coverage == "html":
        command.extend(["--cov=test_envs", "--cov-report=term-missing", "--cov-report=html"])
    return command


def _validate_ollama_test_plan(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("version") != 1:
        raise RuntimeError("Invalid Ollama test plan: version must be 1")
    agent = raw.get("agent")
    selection = raw.get("selection")
    reports = raw.get("reports")
    execution = raw.get("execution")
    if not all(isinstance(value, dict) for value in (agent, selection, reports, execution)):
        raise RuntimeError("Invalid Ollama test plan: agent, selection, reports, and execution must be mappings")
    if agent.get("provider") != "ollama" or not isinstance(agent.get("model"), str) or not agent["model"].strip():
        raise RuntimeError("Invalid Ollama test plan: agent must configure provider 'ollama' and a model")
    pytest_plan = selection.get("pytest")
    unittest_plan = selection.get("unittest")
    if not isinstance(pytest_plan, dict) or not isinstance(unittest_plan, dict):
        raise RuntimeError("Invalid Ollama test plan: pytest and unittest selections are required")
    pytest_mode = pytest_plan.get("mode")
    unittest_mode = unittest_plan.get("mode")
    if pytest_mode not in {"all", "selected"} or unittest_mode not in {"all", "selected"}:
        raise RuntimeError("Invalid Ollama test plan: selection mode must be all or selected")
    pytest_ids = pytest_plan.get("test_ids", [])
    unittest_scopes = unittest_plan.get("scopes", [])
    if not isinstance(pytest_ids, list) or not all(isinstance(item, str) for item in pytest_ids):
        raise RuntimeError("Invalid Ollama test plan: pytest test_ids must be a string list")
    if not isinstance(unittest_scopes, list) or not all(isinstance(item, str) for item in unittest_scopes):
        raise RuntimeError("Invalid Ollama test plan: unittest scopes must be a string list")
    test_ids = catalog_by_id()
    if pytest_mode == "selected" and (not pytest_ids or any(item not in test_ids for item in pytest_ids)):
        raise RuntimeError("Invalid Ollama test plan: pytest test_ids must be allowlisted and non-empty")
    if unittest_mode == "selected" and (not unittest_scopes or any(item not in UNITTEST_SCOPES for item in unittest_scopes)):
        raise RuntimeError("Invalid Ollama test plan: unittest scopes must be declared and non-empty")
    fixture_mode = pytest_plan.get("fixture_mode", "marker")
    coverage = execution.get("coverage", "none")
    pandoc = reports.get("pandoc", "none")
    timeout_seconds = execution.get("timeout_seconds", 3600)
    if fixture_mode not in {"marker", "mock", "hil"}:
        raise RuntimeError("Invalid Ollama test plan: unsupported fixture_mode")
    if coverage not in {"none", "terminal", "html"}:
        raise RuntimeError("Invalid Ollama test plan: unsupported coverage")
    if pandoc not in {"none", "docx", "html", "both"}:
        raise RuntimeError("Invalid Ollama test plan: unsupported Pandoc format")
    if not isinstance(reports.get("markdown"), bool):
        raise RuntimeError("Invalid Ollama test plan: reports.markdown must be true or false")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 3600:
        raise RuntimeError("Invalid Ollama test plan: timeout_seconds must be between 1 and 3600")
    return {
        "version": 1,
        "agent": {"provider": "ollama", "model": agent["model"].strip()},
        "selection": {
            "pytest": {"mode": pytest_mode, "test_ids": pytest_ids, "fixture_mode": fixture_mode},
            "unittest": {"mode": unittest_mode, "scopes": unittest_scopes},
        },
        "reports": {"markdown": reports["markdown"], "pandoc": pandoc},
        "execution": {"coverage": coverage, "timeout_seconds": timeout_seconds},
    }


def _validate(request: TestRequest, timeout_seconds: int) -> None:
    if request.test_type not in {"pytest", "unittest"}:
        raise ValueError("test_type must be pytest or unittest")
    test_ids = catalog_by_id()
    if request.test_type == "pytest" and request.test_id not in test_ids:
        raise ValueError(f"test_id must be one of: {', '.join(test_ids)}")
    if request.fixture_mode not in {"marker", "mock", "hil"}:
        raise ValueError("fixture_mode must be marker, mock, or hil")
    effective_mode = (
        _marker_mode(request.test_id)
        if request.test_type == "pytest" and request.fixture_mode == "marker"
        else request.fixture_mode
    )
    if request.test_type == "pytest" and effective_mode == "hil" and not _enabled("PYTEST_HIL_ALLOW"):
        raise PermissionError("Pytest HIL execution requires PYTEST_HIL_ALLOW=true")
    if request.unittest_scope not in UNITTEST_SCOPES:
        raise ValueError("unsupported unittest scope")
    if request.coverage not in {"none", "terminal", "html"}:
        raise ValueError("unsupported coverage mode")
    if request.pandoc not in {"none", "docx", "html", "both"}:
        raise ValueError("unsupported Pandoc format")
    if timeout_seconds < 1 or timeout_seconds > 3600:
        raise ValueError("timeout_seconds must be between 1 and 3600")


def _convert_pandoc(markdown_path: Path, output: PandocFormat) -> dict[str, str]:
    formats = ("docx", "html") if output == "both" else (output,)
    return {
        output_format: _relative(convert(markdown_path, output_format))
        for output_format in formats
        if output_format != "none"
    }


def _marker_mode(test_id: str) -> str:
    try:
        return str(catalog_by_id()[test_id]["default_fixture_mode"])
    except KeyError as error:
        raise ValueError(f"Unknown TEST ID: {test_id}") from error


def _default_test_id() -> str:
    tests = catalog_tests()
    if not tests:
        raise RuntimeError("The Pytest test catalog is empty")
    return str(tests[0]["test_id"])


def _enabled(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() == "true"


def _relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)
