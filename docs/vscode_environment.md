# VS Code Environment

<br/>

## VS Code Files

<br/>

Go To [VS Code Testing](https://jeonghunlee.github.io/vscode_doc/#vscode-testing) 

* **VS Code Testing**    
https://code.visualstudio.com/docs/debugtest/testing

<br/>

* **VS Code Testing for Python**     
https://code.visualstudio.com/docs/python/testing  

<br/>

```text
.vscode/
├── settings.json    # Python interpreter, analysis, and Testing
├── launch.json      # Run and Debug configurations
└── tasks.json       # Setup, check, test, report, and MkDocs tasks
```

<br/>

| File | Responsibility |
|---|---|
| `settings.json` | Define project settings for [Testing](#testing) and the [Python Extension](#python-extension) |
| `launch.json` | Define [Run and Debug](#run-and-debug) configurations |
| `tasks.json` | Define [Tasks](#tasks) configurations |

<br/>

There is currently no `.vscode/extensions.json`; extension recommendations are not managed by the repository.

<br/>

### settings

<br/>

* **VS Code Testing for Python**     
https://code.visualstudio.com/docs/python/testing  

<br/>

* Source: `.vscode/settings.json`
Connected VS Code features: [Testing](#testing) and [Python Extension](#python-extension)
```json
{
  //.venv
  //Python Automatic Environment Activation 
  //    true: automatically activate venv  (.\.venv\Scripts\Activate.ps1)
  //    false: do not automatically activate venv  
  "python.terminal.activateEnvironment": false,
  
  //venv path for Python
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  
  //Python Testing Configuration
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

<br/>

| Setting | Current value | Effect |
|---|---|---|
| `python.defaultInterpreterPath` | `${workspaceFolder}/.venv/Scripts/python.exe` | Testing, debugging, and most Tasks use the project virtual environment |
| `python.terminal.activateEnvironment` | `false` | New terminals do not automatically activate the selected environment |
| `python.testing.pytestEnabled` | `true` | VS Code Testing uses the pytest adapter |
| `python.testing.unittestEnabled` | `false` | Prevents duplicate native-unittest discovery |
| `python.testing.pytestArgs` | Cache option plus two test roots | Discovers pytest CT and `unittest.TestCase` through pytest |
| `python.testing.cwd` | `${workspaceFolder}` | Resolves `test_envs.*` imports from the repository root |
| `python.testing.autoTestDiscoverOnSaveEnabled` | `true` | Recollects tests after test-file saves |
| `python.analysis.extraPaths` | `${workspaceFolder}` | Lets Pylance resolve repository packages |

`-p no:cacheprovider` disables pytest's cache provider, so VS Code discovery and execution do not create or update `.pytest_cache`.

<br/>

### tasks 

<br/>

* **Tasks**   
https://code.visualstudio.com/docs/debugtest/tasks

<br/>

* Source: `.vscode/tasks.json`    
Connected VS Code feature: [Run Tasks](#run-tasks)
```
{
    "version": "2.0.0",
    "tasks": [
        //Setup Task Section
        // This section contains tasks for setting up the development environment, including selecting the OS, installing Python virtual environment, and installing Ollama and local LLM.
        // Each task is labeled with a "SETUP" prefix for easy identification.
        {
            "label": "SETUP 1: Select Operating System",
            "type": "process",
            "command": "python",
            "args": [
                "-m",
                "test_envs.tools.configuration",
                "select-os"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "clear": true
            },
            "problemMatcher": []
        },
        {
            "label": "SETUP 2: Install Python Virtual Environment",
            "type": "process",
            "command": "python",
            "args": [
                "-m",
                "test_envs.tools.environment_setup",
                "python"
            ],
            "problemMatcher": []
        },
        {
            "label": "SETUP 3: Install Ollama and Local LLM",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.environment_setup",
                "ollama"
            ],
            "problemMatcher": []
        },
        // Check Task Section
        // This section contains tasks for checking the environment and running the Ollama server.
        // Each task is labeled with a "CHECK" prefix for easy identification.
        {
            "label": "CHECK 1: Refresh Environment Check File",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.configuration",
                "check"
            ],
            "problemMatcher": []
        },
        {
            "label": "CHECK 2: Show Environment Configuration",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.configuration",
                "config"
            ],
            "problemMatcher": []
        },
        {
            "label": "CHECK 3: Run Ollama Server (Foreground)",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.environment_setup",
                "serve"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "clear": true
            },
            "problemMatcher": []
        },
        // Test Case Task Section
        // "TEST CASE" prefix for easy identification and Input Section for test case ID and fixture mode
        {
            "label": "TEST CASE: ALL",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "test_envs/tests/pytest/test_cases",
                "--fixture-mode",
                "${input:fixtureMode}"
            ],
            "group": {
                "kind": "test",
                "isDefault": true
            },
            "problemMatcher": []
        },
        {
            "label": "TEST CASE: TEST ID",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "test_envs/tests/pytest/test_cases",
                "--test-id",
                "${input:testCaseId}",
                "--fixture-mode",
                "${input:fixtureMode}"
            ],
            "group": {
                "kind": "test",
                "isDefault": false
            },
            "problemMatcher": []
        },
        // Report Task Section
        // This section contains tasks for generating and converting test reports.
        // Each task is labeled with a "REPORT" prefix for easy identification.
        {
            "label": "REPORT-Mkdocs: Generate Markdown to Pytest/Unittest",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.test_result",
                "--pending",
                "--docs"
            ],
            "problemMatcher": []
        },
        {
            "label": "REPORT-Pandoc: Convert Latest Markdown to HTML",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.pandoc_reporter",
                "--latest",
                "--format",
                "html"
            ],
            "problemMatcher": []
        },
        {
            "label": "REPORT-Pandoc: Convert Latest Markdown to DOCX",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "test_envs.tools.pandoc_reporter",
                "--latest",
                "--format",
                "docx"
            ],
            "problemMatcher": []
        },
        // MkDocs Task Section
        // This section contains tasks for serving and building MkDocs documentation.
        // Each task is labeled with a "MkDocs" prefix for easy identification.
        {
            "label": "MkDocs: Serve Local 8000",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "mkdocs",
                "serve"
            ],
            "problemMatcher": []
        },
        {
            "label": "MkDocs: Serve Local 8080",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "mkdocs",
                "serve",
                "-a",
                "0.0.0.0:8080"
            ],
            "problemMatcher": []
        },
        {
            "label": "MkDocs: Serve Remote ",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "mkdocs",
                "serve",
                "-a",
                "0.0.0.0:8000"
            ],
            "problemMatcher": []
        },
        {
            "label": "MkDocs: Build",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "mkdocs",
                "build"
            ]
        },
        {
            "label": "MkDocs: Build Strict",
            "type": "process",
            "command": "${config:python.defaultInterpreterPath}",
            "args": [
                "-m",
                "mkdocs",
                "build",
                "--strict"
            ]
        }
    ],
    // End of tasks array
    // End of tasks section

    // Inputs section (Test case and fixture mode inputs)
    // "TEST CASE: TEST ID", and "TEST CASE: ALL"
    "inputs": [
        {
            "id": "testCaseId",
            "type": "pickString",
            "description": "TEST ID",
            "options": [
                "CT-UART-001",
                "CT-USB-001",
                "CT-NETWORK-001"
            ],
            "default": "CT-UART-001"
        },
        {
            "id": "fixtureMode",
            "type": "pickString",
            "description": "Fixture mode",
            "options": [
                "marker",
                "mock",
                "hil"
            ],
            "default": "marker"
        }
    ]
}

```

<br/>

### launch

<br/>

* **Run and Debug**
https://code.visualstudio.com/docs/debugtest/debugging
https://code.visualstudio.com/docs/debugtest/debugging-configuration

<br/>

* Source: `.vscode/launch.json`
Connected VS Code feature: [Run and Debug](#run-and-debug)
```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "SETUP 1: Select Operating System",
      "type": "debugpy",
      "request": "launch",
      "python": "python",
      "module": "test_envs.tools.configuration",
      "args": ["config"],
      "preLaunchTask": "SETUP 1: Select Operating System",
      "console": "internalConsole",
      "internalConsoleOptions": "neverOpen",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "SETUP 2: Install Python Virtual Environment",
      "type": "debugpy",
      "request": "launch",
      "python": "python",
      "module": "test_envs.tools.configuration",
      "args": ["config"],
      "preLaunchTask": "SETUP 2: Install Python Virtual Environment",
      "console": "internalConsole",
      "internalConsoleOptions": "neverOpen",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "SETUP 3: Install Ollama and Local LLM",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "test_envs.tools.configuration",
      "args": ["config"],
      "preLaunchTask": "SETUP 3: Install Ollama and Local LLM",
      "console": "internalConsole",
      "internalConsoleOptions": "neverOpen",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "CHECK 1: Refresh Environment Check File",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "test_envs.tools.configuration",
      "args": ["config"],
      "preLaunchTask": "CHECK 1: Refresh Environment Check File",
      "console": "internalConsole",
      "internalConsoleOptions": "neverOpen",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "Run 1: Extension Module",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "test_envs.tools.extension_runner",
      "args": ["--module", "test_envs.tools.extensions.example"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "REPORT-Mkdocs: Generate Markdown to Pytest/Unittest",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "test_envs.tools.test_result",
      "args": ["--pending", "--docs"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "REPORT-Pandoc: Convert Latest Markdown to HTML",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "test_envs.tools.pandoc_reporter",
      "args": ["--latest", "--format", "html"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "REPORT-Pandoc: Convert Latest Markdown to DOCX",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "test_envs.tools.pandoc_reporter",
      "args": ["--latest", "--format", "docx"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "Debug: Current Python File",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "program": "${file}",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": true
    },
    {
      "name": "Debug: Current pytest File",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "pytest",
      "args": ["${file}", "-s", "-vv", "--fixture-mode", "${input:fixtureMode}"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": false
    },
    {
      "name": "TEST CASE: CT-UART-001",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "pytest",
      "args": ["-p", "no:cacheprovider", "test_envs/tests/pytest/test_cases", "--test-id", "CT-UART-001", "--fixture-mode", "${input:fixtureMode}", "-s", "-vv"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": false
    },
    {
      "name": "TEST CASE: CT-USB-001",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "pytest",
      "args": ["-p", "no:cacheprovider", "test_envs/tests/pytest/test_cases", "--test-id", "CT-USB-001", "--fixture-mode", "${input:fixtureMode}", "-s", "-vv"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": false
    },
    {
      "name": "TEST CASE: CT-NETWORK-001",
      "type": "debugpy",
      "request": "launch",
      "python": "${config:python.defaultInterpreterPath}",
      "module": "pytest",
      "args": ["-p", "no:cacheprovider", "test_envs/tests/pytest/test_cases", "--test-id", "CT-NETWORK-001", "--fixture-mode", "${input:fixtureMode}", "-s", "-vv"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "justMyCode": false
    }
  ],
  "inputs": [
    {
      "id": "fixtureMode",
      "type": "pickString",
      "description": "Fixture mode",
      "options": ["marker", "mock", "hil"],
      "default": "marker"
    }
  ]
}

```

<br/>


## Run and Debug

<br/>

Source: `.vscode/launch.json`

![VS Code Run and Debug panel](imgs/vscode_runanddebug_00.png)

<br/>

### Configurations

<br/>

| Configuration | Python | Entry point | Console | `justMyCode` | Function |
|---|---|---|---|---:|---|
| `SETUP 1: Select Operating System` | `python` | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Setup Task, then displays configuration |
| `SETUP 2: Install Python Virtual Environment` | `python` | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Setup Task, then displays configuration |
| `SETUP 3: Install Ollama and Local LLM` | Project Python | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Setup Task, then displays configuration |
| `CHECK 1: Refresh Environment Check File` | Project Python | `test_envs.tools.configuration config` | Internal | `true` | Runs the matching Check Task, then displays configuration |
| `Run 1: Extension Module` | Project Python | `test_envs.tools.extension_runner` | Integrated terminal | `true` | Runs `test_envs.tools.extensions.example` |
| `REPORT-Mkdocs: Generate Markdown to Pytest/Unittest` | Project Python | `test_envs.tools.test_result` | Integrated terminal | `true` | Runs `--pending --docs` |
| `REPORT-Pandoc: Convert Latest Markdown to HTML` | Project Python | `test_envs.tools.pandoc_reporter` | Integrated terminal | `true` | Converts the latest Markdown report to HTML |
| `REPORT-Pandoc: Convert Latest Markdown to DOCX` | Project Python | `test_envs.tools.pandoc_reporter` | Integrated terminal | `true` | Converts the latest Markdown report to DOCX |
| `Debug: Current Python File` | Project Python | `${file}` | Integrated terminal | `true` | Debugs the open Python file |
| `Debug: Current pytest File` | Project Python | `pytest` | Integrated terminal | `false` | Debugs the open test with the selected fixture mode |
| `TEST CASE: CT-UART-001` | Project Python | `pytest --test-id CT-UART-001` | Integrated terminal | `false` | Runs or debugs the UART CT with the selected fixture mode |
| `TEST CASE: CT-USB-001` | Project Python | `pytest --test-id CT-USB-001` | Integrated terminal | `false` | Runs or debugs the USB CT with the selected fixture mode |
| `TEST CASE: CT-NETWORK-001` | Project Python | `pytest --test-id CT-NETWORK-001` | Integrated terminal | `false` | Runs or debugs the Network CT with the selected fixture mode |

<br/>

“Project Python” means `${config:python.defaultInterpreterPath}`.

<br/>

### Setup and Check delegation

<br/>

The first four configurations use `preLaunchTask`. The Task performs the state-changing work; after it succeeds, the launch configuration runs `test_envs.tools.configuration config` and exits.

<br/>

| Launch configuration | `preLaunchTask` |
|---|---|
| `SETUP 1: Select Operating System` | Same label |
| `SETUP 2: Install Python Virtual Environment` | Same label |
| `SETUP 3: Install Ollama and Local LLM` | Same label |
| `CHECK 1: Refresh Environment Check File` | Same label |

<br/>

All launch configurations use `${workspaceFolder}` as `cwd`. Setup 1 and Setup 2 deliberately use system `python`; every later configuration uses the interpreter selected by `python.defaultInterpreterPath`.

<br/>

### Current pytest debugging

<br/>

`Debug: Current pytest File` runs:

```text
python -m pytest ${file} -s -vv --fixture-mode <selection>
```

<br/>

The launch input `fixtureMode` offers `marker`, `mock`, and `hil`, with `marker` as the default. `marker` is a selection instruction; the CT itself resolves to `mock` or `hil`.

<br/>

## Run Tasks

<br/>

Source: `.vscode/tasks.json`

![VS Code Tasks](imgs/vscode_task_00.png)

<br/>

Every Task has `type: process`, runs in the foreground, and has no `isBackground` flag. Setup 1 and Setup 2 use system `python`; all later Tasks use `${config:python.defaultInterpreterPath}`.

<br/>

### Tasks-Setup and Check 

<br/>

| Task label | Module | Arguments | Function |
|---|---|---|---|
| `SETUP 1: Select Operating System` | `test_envs.tools.configuration` | `select-os` | Stores the selected OS in project configuration |
| `SETUP 2: Install Python Virtual Environment` | `test_envs.tools.environment_setup` | `python` | Creates `.venv` and installs dependencies |
| `SETUP 3: Install Ollama and Local LLM` | `test_envs.tools.environment_setup` | `ollama` | Installs/checks Ollama and pulls the configured model |
| `CHECK 1: Refresh Environment Check File` | `test_envs.tools.configuration` | `check` | Regenerates `check.json` |
| `CHECK 2: Show Environment Configuration` | `test_envs.tools.configuration` | `config` | Prints the current project configuration |
| `CHECK 3: Run Ollama Server (Foreground)` | `test_envs.tools.environment_setup` | `serve` | Runs an Ollama server owned by the terminal Task |

<br/>

The dedicated-terminal presentation is configured for Setup 1 and Check 3. Closing or stopping Check 3 ends the foreground server process owned by that Task.

<br/>

### Tasks-TEST CASE 

<br/>

| Task label | Scope | Arguments | Test group |
|---|---|---|---|
| `TEST CASE: ALL` | All CT files in `test_cases` | `--fixture-mode ${input:fixtureMode}` | Default test Task |
| `TEST CASE: TEST ID` | One selected TEST ID | `--test-id ${input:testCaseId} --fixture-mode ${input:fixtureMode}` | Non-default test Task |

<br/>

Both Tasks disable the pytest cache provider and execute `test_envs/tests/pytest/test_cases`.

<br/>

### Tasks-Report 

| Task label | Entry point | Function |
|---|---|---|
| `REPORT-Mkdocs: Generate Markdown to Pytest/Unittest` | `test_envs.tools.test_result --pending --docs` | Generates missing Markdown and publishes MkDocs pages |
| `REPORT-Pandoc: Convert Latest Markdown to HTML` | `test_envs.tools.pandoc_reporter --latest --format html` | Converts the latest Markdown to HTML |
| `REPORT-Pandoc: Convert Latest Markdown to DOCX` | `test_envs.tools.pandoc_reporter --latest --format docx` | Converts the latest Markdown to Word |

### Tasks-MkDocs 

| Task label | Arguments | Address / result |
|---|---|---|
| `MkDocs: Serve Local 8000` | `mkdocs serve` | MkDocs default local address and port 8000 |
| `MkDocs: Serve Local 8080` | `mkdocs serve -a 0.0.0.0:8080` | All interfaces, port 8080 |
| `MkDocs: Serve Remote ` | `mkdocs serve -a 0.0.0.0:8000` | All interfaces, port 8000 |
| `MkDocs: Build` | `mkdocs build` | Generates the static site |
| `MkDocs: Build Strict` | `mkdocs build --strict` | Treats build warnings as errors |

The `MkDocs: Serve Remote ` source label currently contains a trailing space.

### Tasks-Inputs 



| Input ID | Type | Options | Default | Used by |
|---|---|---|---|---|
| `testCaseId` | `pickString` | `CT-UART-001`, `CT-USB-001`, `CT-NETWORK-001` | `CT-UART-001` | `TEST CASE: TEST ID` |
| `fixtureMode` | `pickString` | `marker`, `mock`, `hil` | `marker` | Both TEST CASE Tasks |

OS selection is not a Task or launch input. It is managed by `test_envs/configs/config.json` through the Setup 1 command.


## Testing

<br/>

* **Pytest and Unittest**   
![](imgs/vscode_testing_00.png)

* **Testing Coverage**   
![](imgs/vscode_testing_01.png)

<br/>

### Discovery model

<br/>

```text
VS Code Testing
└── Microsoft Python extension
    └── pytest adapter
        ├── test_envs/tests/pytest
        │   └── CT test cases: mock or hil
        └── test_envs/tests/unittest
            └── unittest.TestCase collected by pytest
```

<br/>

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

<br/>

### Discovery lifecycle

<br/>

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
<br/>

| Trigger | Result |
|---|---|
| Workspace open | Initial collection of both configured roots |
| Save a test file | Automatic rediscovery |
| Refresh Tests | Full manual recollection |
| Change Testing settings | Adapter restarts with the new scope |

<br/>

### Execution contracts

<br/>

| Area | Identifier | Mode | Result |
|---|---|---|---|
| pytest CT | TEST ID | Final mode is `mock` or `hil` | `<execution-id>_result.json` + `<execution-id>_test.log` |
| unittest | Test function | Fixture mode is not used | `<execution-id>_result.json` + `<execution-id>_result.log` |

The Testing panel supports running or debugging the full tree, a folder, a module, a class, or one test function. CT normalization is handled by `test_envs/tests/pytest/conftest.py`; unittest normalization is handled by `test_envs/tests/unittest/conftest.py`.

<br/>

### Discovery troubleshooting

<br/>

| Symptom | Check |
|---|---|
| No tests found | Verify both paths in `python.testing.pytestArgs` |
| Import error | Verify the `.venv` interpreter, workspace `cwd`, and `extraPaths` |
| `.venv` missing | Run `SETUP 2: Install Python Virtual Environment` |
| Duplicate unittest nodes | Keep `python.testing.unittestEnabled` set to `false` |
| Cache path warning | Keep `-p no:cacheprovider` in `pytestArgs` |

<br/>

## Python Extension

<br/>

![VS Code Python interpreter](imgs/vscode_python_00.png)

<br/>

| Stage | Interpreter |
|---|---|
| Setup 1: OS selection | System `python` |
| Setup 2: `.venv` creation | System `python` |
| Setup 3 and later | `${workspaceFolder}/.venv/Scripts/python.exe` |
| VS Code Testing | `${workspaceFolder}/.venv/Scripts/python.exe` |
| Python terminal | Automatic environment activation is disabled; activate `.venv` manually when needed |

<br/>
