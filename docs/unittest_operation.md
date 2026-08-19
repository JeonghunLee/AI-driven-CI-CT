# Unittest Operation

## Identifier

| Identifier | Rule | Format |
|---|---|---|
| TEST ID | Not used | - |
| Fixture ID | Not used | - |
| Mode | Not used | - |
| Execution ID | Required | `YYYYMMDD_HHMMSS_ffffff` |

## Runtime

```text
VS Code Testing / pytest adapter
       ↓
unittest conftest hook
       ↓
Function result collection
       ↓
Result JSON + Result log
       ↓
Markdown + MkDocs
```

## Capture

| Item | Value |
|---|---|
| Hook | `test_envs/tests/unittest/conftest.py` |
| Unit | Test Function |
| Source | pytest node ID |
| Path | Test source file path |
| Pass | Boolean + status |
| Failure | Failure detail |

## Result

```text
test_envs/reports/results/unittest/
├── <execution-id>_result.json
└── <execution-id>_result.log
```

```text
execution
├── execution_id
├── timestamp
├── status
├── duration
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
├── path
├── function
├── pass
├── status
├── duration
└── failure
```

## Local LLM

| Item | Rule |
|---|---|
| Usage | Not used |
| Ollama request | Not generated |
| Local LLM log | Not generated |

## Markdown

```text
test_envs/reports/markdown/unittest/<execution-id>_result.md
docs/tests/unittest/<execution-id>.md
```

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

## Index

```text
docs/tests/unittest/index.md
├── Unit Tests
│   ├── Test Function Count
│   ├── Pass
│   └── Latest execution link
└── Recent Executions
    ├── Execution ID link
    ├── Result
    ├── Tests
    ├── Passed
    └── Failed
```

## Report generation

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.test_result --pending --docs
```

| Output | Rule |
|---|---|
| Canonical Markdown | Execution ID |
| MkDocs document | Execution ID |
| Unittest index | Automatic |

## Documents

| Scope | Document |
|---|---|
| unittest | [unittest.md](unittest.md) |
| Results | [tests/unittest/index.md](tests/unittest/index.md) |
