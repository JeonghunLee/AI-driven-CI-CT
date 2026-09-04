# Pytest Operation

<br/>

Pytest executes Fixture-based CT Test Cases in `mock` or `hil` mode. After execution, the Report operation uses a Local LLM to analyze the result and generate Markdown.

<br/>

Framework structure and Fixture contracts are documented in [Pytest CT Framework](pytest_framework.md).

<br/>

## Operation Summary

<br/>

| Item | Pytest operation |
|---|---|
| Test unit | One CT Test Case |
| Primary identifier | TEST ID, such as `CT-UART-001` |
| Test composition | Numbered Fixture with interfaces and equipment |
| Runtime mode | `mock` or `hil` |
| Result capture | `test_envs/tests/pytest/conftest.py` |
| Local LLM | Used during Report generation |
| Coverage | `pytest-cov` or VS Code Testing Coverage |

<br/>

## Execution Sequence

<br/>

```text
Collect CT Test Cases
        ↓
Validate TEST ID, Fixture ID, marker, and Fixture metadata
        ↓
Apply optional --test-id selection
        ↓
Resolve mock or hil mode
        ↓
Connect Fixture interfaces and equipment
        ↓
Execute Test Case and record metrics/statistics
        ↓
Disconnect Fixture resources
        ↓
Write Result JSON and Test Log
```

<br/>

| Step | Operation |
|---:|---|
| 1 | Pytest collects `test_envs/tests/pytest/test_cases` |
| 2 | `conftest.py` validates the CT marker and numbered Fixture contract |
| 3 | `--test-id` keeps one TEST ID when provided |
| 4 | `--fixture-mode` overrides the marker or uses its default mode |
| 5 | The Fixture connects its interface and equipment before `yield` |
| 6 | The Test Case executes assertions and updates `ct_result` |
| 7 | Fixture cleanup disconnects resources in reverse order |
| 8 | The result hook stores normalized evidence by TEST ID and Execution ID |

<br/>

`marker` is a mode-selection instruction, not a final execution mode. It resolves to the `mock` or `hil` value declared by `@pytest.mark.ct`.

<br/>

## Run Pytest

<br/>

Run every configured test:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest
```

<br/>

Run all CT Test Cases with their marker modes:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=marker
```

<br/>

Force Mock mode:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=mock
```

<br/>

Run one TEST ID:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --test-id CT-UART-001 --fixture-mode=mock
```

<br/>

The current executable CT Test Cases use Mock implementations. Selecting HIL fails explicitly where a physical Fixture implementation has not been completed.

<br/>

## Test Coverage

<br/>

Run CT Test Cases and print missing Python lines:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=mock --cov=test_envs --cov-report=term-missing
```

<br/>

`pytest-cov` stores coverage data in `.coverage`. Add `--cov-report=html` when an HTML report under `htmlcov/` is needed.

<br/>

In VS Code Testing, select a Pytest node and use **Run Test with Coverage**. Coverage measures executed Python code; it does not measure physical HIL signal or protocol coverage.

<br/>

## Result and Report

<br/>

Pytest execution and Report generation are separate operations.

<br/>

```text
Pytest execution
      ↓
Result JSON + Test Log
      ↓
test_envs.tools.test_result
      ↓
Local LLM analysis
      ↓
Conditional escalation decision
      ↓
Canonical Markdown
      ├── MkDocs Results
      └── Pandoc Report
```

<br/>

| Output | Path |
|---|---|
| Result JSON | `test_envs/reports/results/pytest/test_cases/<test-id>/<execution-id>_result.json` |
| Test log | `test_envs/reports/results/pytest/test_cases/<test-id>/<execution-id>_test.log` |
| Local LLM log | `test_envs/reports/local_llm/<execution-id>_local_llm.log` |
| Canonical Markdown | `test_envs/reports/markdown/<test-id>/<execution-id>_result.md` |
| MkDocs result | `docs/tests/pytest/` |
| Pandoc output | `test_envs/reports/pandoc/<test-id>/` |

<br/>

Generate every pending Markdown report and publish MkDocs result pages:

<br/>

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.test_result --pending --docs
```

<br/>

If Ollama is unavailable or returns invalid analysis, the reporter records the attempts and uses deterministic fallback analysis so Report generation can continue.

<br/>

See [Pytest Results](tests/pytest/index.md) for published results.

<br/>
