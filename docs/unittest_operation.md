# Unittest Operation

<br/>

Unittest executes Python unit-test functions through the pytest adapter. It records function-level results and generates reports without Local LLM analysis.

<br/>

Framework structure and result contracts are documented in [Unittest Framework](unittest_framework.md).

<br/>

## Operation Summary

<br/>

| Item | Unittest operation |
|---|---|
| Test unit | Test function or `unittest.TestCase` method |
| Primary identifier | Execution ID |
| TEST ID and Fixture ID | Not used |
| Mock/HIL mode | Not used |
| Result capture | `test_envs/tests/unittest/conftest.py` |
| Local LLM | Not used |
| Coverage | `pytest-cov` or VS Code Testing Coverage |

<br/>

## Execution Sequence

<br/>

```text
Collect unittest tests through pytest
        ↓
Execute setup, call, and teardown phases
        ↓
Capture function status, duration, and failure detail
        ↓
Aggregate every function at session finish
        ↓
Write Result JSON and Result Log
```

<br/>

| Step | Operation |
|---:|---|
| 1 | The pytest adapter collects tests under `test_envs/tests/unittest` |
| 2 | The result hook observes setup, call, and teardown reports |
| 3 | Each function becomes `PASS`, `FAIL`, `ERROR`, or `SKIP` |
| 4 | `pytest_sessionfinish` aggregates function results into one execution |
| 5 | The framework stores one Result JSON and Result Log per Execution ID |

<br/>

Setup or teardown failures become `ERROR`. Assertion failures during the call phase become `FAIL`.

<br/>

## Run Unittest

<br/>

Run the complete Unittest area:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider test_envs/tests/unittest
```

<br/>

Run one test file:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider test_envs/tests/unittest/ct_framework/python/test_configuration.py
```

<br/>

VS Code Testing also discovers these tests through the pytest adapter. Native VS Code unittest discovery remains disabled to prevent duplicate nodes.

<br/>

## Test Coverage

<br/>

Run Unittest and print missing Python lines:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider test_envs/tests/unittest --cov=test_envs --cov-report=term-missing
```

<br/>

`pytest-cov` stores coverage data in `.coverage`. Add `--cov-report=html` to generate an HTML report under `htmlcov/`.

<br/>

In VS Code Testing, select the Unittest tree or a test node and use **Run Test with Coverage**.

<br/>

## Result and Report

<br/>

Unittest execution and Report generation are separate operations. The shared Report pipeline detects `category: unit` and skips Local LLM analysis and escalation.

<br/>

```text
Unittest execution
        ↓
Result JSON + Result Log
        ↓
test_envs.tools.test_result
        ↓
Local LLM and escalation: skipped
        ↓
Canonical Markdown
        ├── MkDocs Results
        └── Pandoc Report
```

<br/>

| Output | Path |
|---|---|
| Result JSON | `test_envs/reports/results/unittest/<execution-id>_result.json` |
| Result log | `test_envs/reports/results/unittest/<execution-id>_result.log` |
| Local LLM log | Not generated |
| Canonical Markdown | `test_envs/reports/markdown/unittest/<execution-id>_result.md` |
| MkDocs result | `docs/tests/unittest/` |
| Pandoc output | `test_envs/reports/pandoc/unittest/` |

<br/>

Generate every pending Markdown report and publish MkDocs result pages:

<br/>

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.test_result --pending --docs
```

<br/>

The command is shared with Pytest, but Unittest produces its Markdown directly from the aggregated function results without contacting Ollama.

<br/>

See [Unittest Results](tests/unittest/index.md) for published results.

<br/>
