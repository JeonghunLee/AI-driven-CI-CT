# VS Code Environment

## Files

```text
.vscode/
├── settings.json
├── launch.json
└── tasks.json
```

## Settings

| Item | Value |
|---|---|
| Interpreter | `${workspaceFolder}/.venv/Scripts/python.exe` |
| pytest | Enabled |
| unittest adapter | Disabled |
| Test adapter | pytest |
| pytest path | `test_envs/tests/pytest` |
| unittest path | `test_envs/tests/unittest` |
| Cache provider | Disabled |

```text
VS Code Testing
      ↓
pytest adapter
├── test_envs/tests/pytest
└── test_envs/tests/unittest
```

## Testing

<br/>

![](./imgs/vscode_testing_00.png)  

<br/>


### Adapter

| Item | Value |
|---|---|
| VS Code panel | Testing |
| Adapter | Python pytest |
| `python.testing.pytestEnabled` | `true` |
| `python.testing.unittestEnabled` | `false` |
| Auto discovery | Enabled |
| Working directory | `${workspaceFolder}` |
| Cache provider | Disabled |

### Discovery

```json
{
  "python.testing.pytestArgs": [
    "-p",
    "no:cacheprovider",
    "test_envs/tests/pytest",
    "test_envs/tests/unittest"
  ]
}
```

| Test tree | Source |
|---|---|
| pytest | `test_envs/tests/pytest/test_cases` |
| unittest | `test_envs/tests/unittest` |

### Pytest execution

| Item | Rule |
|---|---|
| Test identification | TEST ID |
| Fixture | `fixture_id` |
| Default mode | Marker `fixture_mode` |
| CLI override | `--fixture-mode` |
| Result | `<execution-id>_result.json` |
| Log | `<execution-id>_test.log` |

### Unittest execution

| Item | Rule |
|---|---|
| Test identification | Function name |
| TEST ID | Not used |
| Fixture mode | Not used |
| Result capture | `test_envs/tests/unittest/conftest.py` |
| Result | `<execution-id>_result.json` |
| Log | `<execution-id>_result.log` |
| Local LLM | Not used |

### Testing actions

| Action | Scope |
|---|---|
| Run All Tests | pytest + unittest |
| Run Test | Selected test/function |
| Debug Test | Selected test/function |
| Refresh Tests | Test discovery |
| Show Test Output | pytest terminal output |

### Result flow

```text
Testing Run
├── pytest
│   ├── TEST ID result
│   └── Test log
└── unittest
    ├── Function results
    └── Result log
         ↓
REPORT: Generate Pending Markdown
         ↓
docs/tests/{pytest,unittest}
```

### Related documents

| Scope | Document |
|---|---|
| Pytest operation | [pytest_operation.md](pytest_operation.md) |
| Unittest operation | [unittest_operation.md](unittest_operation.md) |
| Pytest results | [tests/pytest/index.md](tests/pytest/index.md) |
| Unittest results | [tests/unittest/index.md](tests/unittest/index.md) |

## Run and Debug

<br/>

![](./imgs/vscode_runanddebug_00.png)

<br/>

| Configuration | Interpreter | Action |
|---|---|---|
| `SETUP 1: Select Operating System` | System Python | OS selection Task |
| `SETUP 2: Install Python Virtual Environment` | System Python | Python setup Task |
| `SETUP 3: Install Ollama and Local LLM` | Project Python | Ollama setup Task |
| `CHECK 1: Refresh Environment Check File` | Project Python | Check Task |
| `Run 1: Extension Module` | Project Python | Extension entry point |
| `Test Result: Generate Pending Markdown` | Project Python | Pending reports |
| `Debug: Current Python File` | Project Python | Current file |
| `Debug: Current pytest File` | Project Python | Current pytest file |

## Tasks

| Group | Label |
|---|---|
| SETUP | `SETUP 1: Select Operating System` |
| SETUP | `SETUP 2: Install Python Virtual Environment` |
| SETUP | `SETUP 3: Install Ollama and Local LLM` |
| CHECK | `CHECK 1: Refresh Environment Check File` |
| CHECK | `CHECK 2: Show Environment Configuration` |
| CHECK | `CHECK 3: Run Ollama Server (Foreground)` |
| TEST CASE | `TEST CASE: ALL` |
| TEST CASE | `TEST CASE: TEST ID` |
| REPORT | `REPORT: Generate Pending Markdown` |
| REPORT | `REPORT: Convert Latest Markdown to HTML` |
| REPORT | `REPORT: Convert Latest Markdown to DOCX` |
| MkDocs | `MkDocs: Serve Locally` |
| MkDocs | `MkDocs: Serve on Network` |
| MkDocs | `MkDocs: Build` |
| MkDocs | `MkDocs: Build Strict` |

## Process lifecycle

| Rule | Value |
|---|---|
| Task type | `process` |
| Background flag | None |
| Ollama server | Foreground |
| Setup/Check launch | `preLaunchTask` delegation |
| OS metadata in Task/Launch | Prohibited |

## Inputs

| ID | Options |
|---|---|
| `testCaseId` | `CT-UART-001`, `CT-USB-001`, `CT-NETWORK-001` |
| `fixtureMode` | `marker`, `mock`, `hil` |

## Reports

| Item | Value |
|---|---|
| Pending command | `python -m test_envs.tools.test_result --pending --docs` |
| Progress interval | 1 second |
| HTML | Pandoc |
| DOCX | Pandoc |
