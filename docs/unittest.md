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

| Runtime | Result capture |
|---|---|
| pytest adapter | `test_envs/tests/unittest/conftest.py` |
| VS Code Testing | pytest adapter |
| Native `python -m unittest` | Result capture not applied |

## Result files

```text
test_envs/reports/results/unittest/
├── <execution-id>_result.json
└── <execution-id>_result.log
```

| File | Source |
|---|---|
| `<execution-id>_result.json` | unittest function reports |
| `<execution-id>_result.log` | Function status + failure detail |

## Result JSON

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

## Markdown

```text
test_envs/reports/markdown/unittest/<execution-id>_result.md
docs/tests/unittest/<execution-id>.md
```

```text
# unittest Result
├── Execution Summary
├── Test Functions
├── Failed Functions
├── Test Source
├── Logs
└── Local LLM Analysis
```

## Index

| Column | Source |
|---|---|
| Test Function | `test_functions[].function` |
| Pass | Latest function status |
| Latest | Latest Seoul timestamp date |
| Test Function Count | Function execution count |
