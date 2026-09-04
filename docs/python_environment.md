# Python Environment

<br/>

The project uses system Python for initial setup and the project-local `.venv` for normal test and report execution.

<br/>

## Python Usage

<br/>

| Stage | Python | Purpose |
|---|---|---|
| OS selection | System Python | Selects the host OS before `.venv` is required |
| Virtual environment creation | System Python | Creates `.venv` and installs project dependencies |
| Pytest and Unittest | Project Python | Runs tests in an isolated environment |
| Environment and report tools | Project Python | Runs `test_envs.tools.*` modules |
| VS Code Testing | Project Python | Discovers and executes tests through pytest |

<br/>

| OS | Project Python |
|---|---|
| Windows | `.venv/Scripts/python.exe` |
| Linux | `.venv/bin/python` |
| macOS | `.venv/bin/python` |

<br/>

## VS Code Usage

<br/>

| VS Code entry | Interpreter | Operation |
|---|---|---|
| `SETUP 1: Select Operating System` | System Python | Selects the OS through the matching Task |
| `SETUP 2: Install Python Virtual Environment` | System Python | Creates `.venv` through the matching Task |
| `SETUP 3: Install Ollama and Local LLM` | Project Python | Installs the Local LLM environment after `.venv` exists |
| VS Code Testing | Project Python | Discovers pytest and unittest tests through pytest |
| Report Tasks | Project Python | Generates Markdown, MkDocs, HTML, and DOCX reports |

<br/>

VS Code uses `python.defaultInterpreterPath` from `.vscode/settings.json`.

<br/>

| OS | VS Code interpreter setting |
|---|---|
| Windows | `${workspaceFolder}/.venv/Scripts/python.exe` |
| Linux | `${workspaceFolder}/.venv/bin/python` |
| macOS | `${workspaceFolder}/.venv/bin/python` |

<br/>

Automatic terminal activation is disabled with `python.terminal.activateEnvironment: false`. Use the explicit project Python path or activate `.venv` manually when needed.

<br/>

See [VS Code Environment](vscode_environment.md) for Settings, Run and Debug, Run Tasks, and Testing configuration.

<br/>

## Configuration and Status

<br/>

### config.json

<br/>

`test_envs/configs/config.json` stores user-selected project configuration.

<br/>

| Key | Role |
|---|---|
| `version` | Configuration schema version |
| `os` | Platform used by environment setup |
| `time` | Report timezone and UTC offset |
| `ollama` | Local LLM endpoint, model, prompt, timeout, and retry settings |

<br/>

### check.json

<br/>

`test_envs/configs/check.json` records detected runtime status.

<br/>

| Section | Recorded status |
|---|---|
| `generated_at` | Time of the latest environment check |
| `os` | Configured OS, detected OS, and host platform name |
| `python` | Installation status, executable path, and version |
| `ollama` | Executable, endpoint, selected model, and installed models |

<br/>

`check.json` is generated data. Change `config.json` and rerun the check command instead of manually editing `check.json`.

<br/>

## Usage Rules

<br/>

| Rule | Reason |
|---|---|
| Run commands from the repository root | `test_envs` imports and repository-relative paths depend on it |
| Use system Python for Setup 1 and Setup 2 | The project environment may not exist yet |
| Use `.venv` Python after setup | Keeps project dependencies isolated from global packages |
| Keep `.venv` out of Git | It is reproducible from `requirements.txt` |
| Do not manually edit `check.json` | It is regenerated from detected runtime state |

<br/>

## Troubleshooting

<br/>

| Symptom | Check |
|---|---|
| `No module named test_envs` | Run the command from the repository root |
| Configured platform does not match host | Set `os` to `auto` or the current host OS |
| `.venv` Python is missing | Run Setup 2 with system Python |
| pip installation fails | Verify network access and `requirements.txt` |
| `Invalid VS Code settings` during OS selection | The configuration tool currently reads `.vscode/settings.json` with a strict JSON parser; JSONC comments are not accepted |
| Test discovery imports fail | Verify the project interpreter and workspace root |

<br/>

## Environment Installation

<br/>

### Requirements

<br/>

| Requirement | Purpose |
|---|---|
| System Python | Provides `venv` and `ensurepip` |
| Repository root | Contains `requirements.txt` and `test_envs/` |
| Network access | Downloads missing Python packages |
| Windows PowerShell | Runs the Windows examples below |

<br/>

Python setup does not install Ollama or a Local LLM. See [Local LLM Environment](local_llm_environment.md) for that installation.

<br/>

### Windows PowerShell

<br/>

Run each command from the repository root.

<br/>

Select the operating system:

<br/>

```powershell
python -m test_envs.tools.configuration select-os
```

<br/>

Create or update `.venv`:

<br/>

```powershell
python -m test_envs.tools.environment_setup python --platform config
```

<br/>

Verify project Python:

<br/>

```powershell
.\.venv\Scripts\python.exe --version
```

<br/>

Refresh environment status:

<br/>

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.configuration check
```

<br/>

Verify test discovery:

<br/>

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --collect-only
```

<br/>

For non-interactive Windows OS selection:

<br/>

```powershell
python -m test_envs.tools.configuration set-os --os windows
```

<br/>

### Linux and macOS

<br/>

```bash
python3 -m test_envs.tools.configuration select-os
```

<br/>

```bash
python3 -m test_envs.tools.environment_setup python --platform config
```

<br/>

```bash
./.venv/bin/python -m test_envs.tools.configuration check
```

<br/>

### Installation Flow

<br/>

`test_envs.tools.environment_setup python` performs these operations:

<br/>

```text
Resolve configured platform
        ↓
Verify configured OS matches the host OS
        ↓
Create .venv when missing
        ↓
Run ensurepip --upgrade
        ↓
Upgrade pip
        ↓
Install requirements.txt
        ↓
Refresh test_envs/configs/check.json
```

<br/>

An existing `.venv` is reused. The command still installs `requirements.txt` again, so it can be rerun after dependency changes.

<br/>

### Installed Packages

<br/>

| Requirement | Purpose |
|---|---|
| `pytest` | Runs CT and unit tests |
| `pytest-cov` | Produces Python coverage data |
| `mkdocs` | Builds and serves documentation |
| `mkdocs-material` | Provides the documentation theme |
| `mkdocs-mermaid2-plugin` | Renders Mermaid diagrams |
| `pyserial` | Supports UART interfaces |
| `pyusb` | Supports USB interfaces |

<br/>

The authoritative package versions are defined in `requirements.txt`.

<br/>

## Full test_envs Structure

<br/>

```text
test_envs/
├── configs/
│   ├── config.json                 # Selected OS, timezone, and Ollama settings
│   └── check.json                  # Detected environment status
├── tests/
│   ├── fixtures/
│   │   └── junit.xml               # Shared result fixture
│   ├── pytest/
│   │   ├── conftest.py             # TEST ID and mock/hil normalization
│   │   ├── fixtures/               # Equipment/interface combinations
│   │   ├── test_cases/             # CT-UART, CT-USB, and CT-NETWORK
│   │   ├── test_equipments/
│   │   │   ├── fpga/{mock,hil}/
│   │   │   ├── saleae/{mock,hil}/
│   │   │   └── digilent/{mock,hil}/
│   │   └── test_interfaces/
│   │       ├── usb/{mock,hil}/
│   │       ├── uart/{mock,hil}/
│   │       ├── jtag/{mock,hil}/
│   │       └── network/{mock,hil}/
│   └── unittest/
│       ├── conftest.py             # Unittest result normalization
│       └── ct_framework/python/    # Current Python framework tests
├── tools/
│   ├── configuration/              # config, check, set-os, and select-os
│   ├── environment_setup.py        # Python and Ollama setup
│   ├── extension_runner.py         # Future extension execution
│   ├── extensions/                 # Extension modules
│   ├── local_llm/                  # Local LLM client and status
│   ├── test_result/                # Pending-result processing
│   ├── mkdocs_reporter/            # MkDocs Markdown publishing
│   ├── pandoc_reporter/            # HTML, DOCX, and PDF conversion
│   ├── github_reporter/            # GitHub reporting
│   ├── result_normalizer/          # Common result model
│   ├── issue_parser.py
│   ├── log_parser/
│   └── pipeline.py
└── reports/
    ├── results/{pytest,unittest}/   # Result JSON and execution logs
    ├── markdown/                    # Generated Markdown reports
    ├── pandoc/                      # Generated HTML, DOCX, or PDF
    └── local_llm/                   # Local LLM analysis artifacts
```

<br/>

The `{mock,hil}` notation means that each listed equipment or interface provides separate `mock/` and `hil/` implementations. Pytest CT execution ultimately resolves to one of these two modes.

<br/>
