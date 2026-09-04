# unittest

## Scope

| Item | Rule |
|---|---|
| TEST ID | Not used |
| Fixture mode | Not used |
| Identifier | Execution ID |
| Result unit | Test Function |
| Pass value | `PASS`, `FAIL` |
| Failure search | `test_functions[].pass == false` |

## Execution

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/unittest
```
<br/>

| Runtime | Result capture |
|---|---|
| pytest adapter | `test_envs/tests/unittest/conftest.py` |
| VS Code Testing | pytest adapter |
| Native `python -m unittest` | Result capture not applied |

<br/>

## Result files

<br/>

```text
test_envs/reports/results/unittest/
├── <execution-id>_result.json
└── <execution-id>_result.log
```

<br/>

| File | Source |
|---|---|
| `<execution-id>_result.json` | unittest function reports |
| `<execution-id>_result.log` | Function status + failure detail |

<br/>

## Result JSON

<br/>

```text
execution
├── execution_id
├── timestamp
├── status
├── duration
├── environment
├── runner
├── commit
├── branch
└── logs
summary
├── total
├── passed
├── failed
├── errors
└── skipped
test_functions[]
├── function
├── pass
├── status
├── duration
└── failure
```

<br/>

## Markdown

<br/>

```text
test_envs/reports/markdown/unittest/<execution-id>_result.md
docs/tests/unittest/<execution-id>.md
```

<br/>

```text
# unittest Result
└── Test Summary
    ├── Test Functions
    │   ├── PATH directory mapping
    │   └── Function result table
    ├── Failed Functions
    ├── Test Source
    └── Logs
```

<br/>

| Local LLM | Rule |
|---|---|
| Ollama request | Not used |
| Analysis | Not used |
| Local LLM log | Not generated |

<br/>

## Index

<br/>

| Column | Source |
|---|---|
| Test Function Count | Latest `summary.total` |
| Pass | Latest Execution status |
| Latest | Latest Seoul timestamp date + Execution document link |

| Recent Executions column | Source |
|---|---|
| Execution ID | Execution document link |
| Result | Execution status |
| Tests | `summary.total` |
| Passed | `summary.passed` |
| Failed | `summary.failed + summary.errors` |

<br/>