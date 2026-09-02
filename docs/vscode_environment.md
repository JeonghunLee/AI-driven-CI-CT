# VS Code Environment

## VS Code Files

```text
.vscode/
├── settings.json    # Python interpreter, analysis, and Testing
├── launch.json      # Run and Debug configurations
└── tasks.json       # Setup, check, test, report, and MkDocs tasks
```

| File | Responsibility |
|---|---|
| `settings.json` | Define Project [Settings](#settings) configurations  |
| `launch.json` | Define [Run and Debug](#run-and-debug) configurations |
| `tasks.json` | Define [Tasks](#tasks) configurations  |

There is currently no `.vscode/extensions.json`; extension recommendations are not managed by the repository.

### Settings

Source: `.vscode/settings.json`

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "-p",
    "no:cacheprovider",
    "test_envs/tests/pytest",
    "test_envs/tests/unittest"
  ],
  "python.testing.cwd": "${workspaceFolder}",
  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "python.analysis.extraPaths": [
    "${workspaceFolder}"
  ]
}
```

| Setting | Current value | Effect |
|---|---|---|
| `python.defaultInterpreterPath` | `${workspaceFolder}/.venv/Scripts/python.exe` | Testing, debugging, and most Tasks use the project virtual environment |
| `python.terminal.activateEnvironment` | `true` | New Python terminals activate the selected environment |
| `python.testing.pytestEnabled` | `true` | VS Code Testing uses the pytest adapter |
| `python.testing.unittestEnabled` | `false` | Prevents duplicate native-unittest discovery |
| `python.testing.pytestArgs` | Cache option plus two test roots | Discovers pytest CT and `unittest.TestCase` through pytest |
| `python.testing.cwd` | `${workspaceFolder}` | Resolves `test_envs.*` imports from the repository root |
| `python.testing.autoTestDiscoverOnSaveEnabled` | `true` | Recollects tests after test-file saves |
| `python.analysis.extraPaths` | `${workspaceFolder}` | Lets Pylance resolve repository packages |

`-p no:cacheprovider` disables pytest's cache provider, so VS Code discovery and execution do not create or update `.pytest_cache`.

## Run and Debug

Source: `.vscode/launch.json`

![VS Code Run and Debug panel](imgs/vscode_runanddebug_00.png)


### Configurations

| Configuration | Python | Entry point | Console | `justMyCode` | Function |
|---|---|---|---|---:|---|
| `SETUP 1: Select Operating System` | `python` | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Setup Task, then displays configuration |
| `SETUP 2: Install Python Virtual Environment` | `python` | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Setup Task, then displays configuration |
| `SETUP 3: Install Ollama and Local LLM` | Project Python | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Setup Task, then displays configuration |
| `CHECK 1: Refresh Environment Check File` | Project Python | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Check Task, then displays configuration |
| `Run 1: Extension Module` | Project Python | `test_envs.tools.extension_runner` | Integrated terminal | `true` | Runs `test_envs.tools.extensions.example` |
| `Test Result: Generate Pending Markdown` | Project Python | `test_envs.tools.test_result` | Integrated terminal | `true` | Runs `--pending --docs` |
| `Debug: Current Python File` | Project Python | `${file}` | Integrated terminal | `true` | Debugs the open Python file |
| `Debug: Current pytest File` | Project Python | `pytest` | Integrated terminal | `false` | Debugs the open test with the selected fixture mode |

“Project Python” means `${config:python.defaultInterpreterPath}`.

### Setup and Check delegation

The first four configurations use `preLaunchTask`. The Task performs the state-changing work; after it succeeds, the launch configuration runs `test_envs.tools.configuration config` and exits.

| Launch configuration | `preLaunchTask` |
|---|---|
| `SETUP 1: Select Operating System` | Same label |
| `SETUP 2: Install Python Virtual Environment` | Same label |
| `SETUP 3: Install Ollama and Local LLM` | Same label |
| `CHECK 1: Refresh Environment Check File` | Same label |

All launch configurations use `${workspaceFolder}` as `cwd`. Setup 1 and Setup 2 deliberately use system `python`; every later configuration uses the interpreter selected by `python.defaultInterpreterPath`.

### Current pytest debugging

`Debug: Current pytest File` runs:

```text
python -m pytest ${file} -s -vv --fixture-mode <selection>
```

The launch input `fixtureMode` offers `marker`, `mock`, and `hil`, with `marker` as the default. `marker` is a selection instruction; the CT itself resolves to `mock` or `hil`.

## Tasks

Source: `.vscode/tasks.json`

![VS Code Tasks](imgs/vscode_task_00.png)


Every Task has `type: process`, runs in the foreground, and has no `isBackground` flag. Setup 1 and Setup 2 use system `python`; all later Tasks use `${config:python.defaultInterpreterPath}`.

### Setup and Check Tasks

| Task label | Module | Arguments | Function |
|---|---|---|---|
| `SETUP 1: Select Operating System` | `test_envs.tools.configuration` | `select-os` | Stores the selected OS in project configuration |
| `SETUP 2: Install Python Virtual Environment` | `test_envs.tools.environment_setup` | `python` | Creates `.venv` and installs dependencies |
| `SETUP 3: Install Ollama and Local LLM` | `test_envs.tools.environment_setup` | `ollama` | Installs/checks Ollama and pulls the configured model |
| `CHECK 1: Refresh Environment Check File` | `test_envs.tools.configuration` | `check` | Regenerates `check.json` |
| `CHECK 2: Show Environment Configuration` | `test_envs.tools.configuration` | `config` | Prints the current project configuration |
| `CHECK 3: Run Ollama Server (Foreground)` | `test_envs.tools.environment_setup` | `serve` | Runs an Ollama server owned by the terminal Task |

The dedicated-terminal presentation is configured for Setup 1 and Check 3. Closing or stopping Check 3 ends the foreground server process owned by that Task.

### TEST CASE Tasks

| Task label | Scope | Arguments | Test group |
|---|---|---|---|
| `TEST CASE: ALL` | All CT files in `test_cases` | `--fixture-mode ${input:fixtureMode}` | Default test Task |
| `TEST CASE: TEST ID` | One selected TEST ID | `--test-id ${input:testCaseId} --fixture-mode ${input:fixtureMode}` | Non-default test Task |

Both Tasks disable the pytest cache provider and execute `test_envs/tests/pytest/test_cases`.

### Report Tasks

| Task label | Entry point | Function |
|---|---|---|
| `REPORT-Mkdocs: Generate Markdown to Pytest/Unittest` | `test_envs.tools.test_result --pending --docs` | Generates missing Markdown and publishes MkDocs pages |
| `REPORT-Pandoc: Convert Latest Markdown to HTML` | `test_envs.tools.pandoc_reporter --latest --format html` | Converts the latest Markdown to HTML |
| `REPORT-Pandoc: Convert Latest Markdown to DOCX` | `test_envs.tools.pandoc_reporter --latest --format docx` | Converts the latest Markdown to Word |

### MkDocs Tasks

| Task label | Arguments | Address / result |
|---|---|---|
| `MkDocs: Serve Local 8000` | `mkdocs serve` | MkDocs default local address and port 8000 |
| `MkDocs: Serve Local 8080` | `mkdocs serve -a 0.0.0.0:8080` | All interfaces, port 8080 |
| `MkDocs: Serve Remote ` | `mkdocs serve -a 0.0.0.0:8000` | All interfaces, port 8000 |
| `MkDocs: Build` | `mkdocs build` | Generates the static site |
| `MkDocs: Build Strict` | `mkdocs build --strict` | Treats build warnings as errors |

The `MkDocs: Serve Remote ` source label currently contains a trailing space.

### Task inputs

| Input ID | Type | Options | Default | Used by |
|---|---|---|---|---|
| `testCaseId` | `pickString` | `CT-UART-001`, `CT-USB-001`, `CT-NETWORK-001` | `CT-UART-001` | `TEST CASE: TEST ID` |
| `fixtureMode` | `pickString` | `marker`, `mock`, `hil` | `marker` | Both TEST CASE Tasks |

OS selection is not a Task or launch input. It is managed by `test_envs/configs/config.json` through the Setup 1 command.


## Testing

![VS Code Testing panel](imgs/vscode_testing_00.png)

### Discovery model

```text
VS Code Testing
└── Microsoft Python extension
    └── pytest adapter
        ├── test_envs/tests/pytest
        │   └── CT test cases: mock or hil
        └── test_envs/tests/unittest
            └── unittest.TestCase collected by pytest
```

| Component | Current rule |
|---|---|
| Adapter | pytest only |
| Interpreter | Project `.venv` |
| Working directory | Workspace root |
| CT root | `test_envs/tests/pytest` |
| unittest root | `test_envs/tests/unittest` |
| File pattern | `test_*.py` from `pytest.ini` |
| Automatic discovery | Enabled on save |
| Cache provider | Disabled |

### Discovery lifecycle

```text
Open workspace
      ↓
Load settings.json
      ↓
Select .venv/Scripts/python.exe
      ↓
Run pytest collection from workspace root
      ↓
Build the unified Testing tree
```

| Trigger | Result |
|---|---|
| Workspace open | Initial collection of both configured roots |
| Save a test file | Automatic rediscovery |
| Refresh Tests | Full manual recollection |
| Change Testing settings | Adapter restarts with the new scope |

### Execution contracts

| Area | Identifier | Mode | Result |
|---|---|---|---|
| pytest CT | TEST ID | Final mode is `mock` or `hil` | `<execution-id>_result.json` + `<execution-id>_test.log` |
| unittest | Test function | Fixture mode is not used | `<execution-id>_result.json` + `<execution-id>_result.log` |

The Testing panel supports running or debugging the full tree, a folder, a module, a class, or one test function. CT normalization is handled by `test_envs/tests/pytest/conftest.py`; unittest normalization is handled by `test_envs/tests/unittest/conftest.py`.

### Discovery troubleshooting

| Symptom | Check |
|---|---|
| No tests found | Verify both paths in `python.testing.pytestArgs` |
| Import error | Verify the `.venv` interpreter, workspace `cwd`, and `extraPaths` |
| `.venv` missing | Run `SETUP 2: Install Python Virtual Environment` |
| Duplicate unittest nodes | Keep `python.testing.unittestEnabled` set to `false` |
| Cache path warning | Keep `-p no:cacheprovider` in `pytestArgs` |


## Python

![VS Code Python interpreter](imgs/vscode_python_00.png)

| Stage | Interpreter |
|---|---|
| Setup 1: OS selection | System `python` |
| Setup 2: `.venv` creation | System `python` |
| Setup 3 and later | `${workspaceFolder}/.venv/Scripts/python.exe` |
| VS Code Testing | `${workspaceFolder}/.venv/Scripts/python.exe` |
| Python terminal | Selected environment, automatically activated |

## Result Flow

```text
VS Code Testing or TEST CASE Task
├── pytest CT
│   ├── TEST ID result JSON
│   └── test log
└── unittest
    ├── execution result JSON
    └── result log
         ↓
REPORT-Mkdocs: Generate Markdown to Pytest/Unittest
         ↓
docs/tests/{pytest,unittest}
```

## Related Documents

| Scope | Document |
|---|---|
| Pytest framework | [pytest.md](pytest.md) |
| Pytest operation | [pytest_operation.md](pytest_operation.md) |
| Unittest operation | [unittest_operation.md](unittest_operation.md) |
| Pytest results | [tests/pytest/index.md](tests/pytest/index.md) |
| Unittest results | [tests/unittest/index.md](tests/unittest/index.md) |
