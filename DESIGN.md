# AI-driven Continuous Testing Architecture

## 1. Core Principles

| Item | Definition |
|---|---|
| Development front-end | VS Code |
| Python runtime | Project-local `.venv` |
| Unit test | `unittest` |
| Continuous test | `pytest` |
| Local LLM runtime | Ollama |
| Primary model | Configurable Ollama model |
| Escalation agent | Codex |
| Human-readable result | Markdown |
| Web documentation | MkDocs |
| Document conversion | Pandoc |
| General automation | GitHub-hosted runner |
| Special environment | Optional self-hosted runner |

```text
CT = Test + Analysis + Documentation
```

## 2. Overall Architecture

```text
VS Code
├── Run and Debug
│   ├── Setup Task Delegation
│   ├── Check Task Delegation
│   ├── Extension Module
│   ├── Latest Markdown Report
│   ├── Current Python Debug
│   └── Current pytest Debug
├── Testing
│   ├── tests/pytest
│   └── tests/unittest
└── Tasks
    ├── Setup / Check
    ├── Foreground Ollama Server
    ├── Test
    ├── Report
    ├── MkDocs
    └── Pandoc
          │
          ▼
        .venv
          │
          ▼
unittest / pytest
          │
          ▼
Result + Log + Measurement + Warning
          │
          ▼
Ollama + Local LLM
          │
          ├── Test Analysis
          ├── Log Analysis
          ├── Warning Analysis
          ├── Source Review
          └── Result Documentation
          │
          ▼
Markdown
├── reports/markdown
├── test_result/markdown/latest.md
├── MkDocs
├── Pandoc
└── GitHub Issue

Complex Failure
      │
      ▼
    Codex
```

## 3. VS Code Run and Debug

Source: `.vscode/launch.json`

| Order | Configuration | Runtime | Entry point | Purpose |
|---:|---|---|---|---|
| 1 | `Setup 1: Select Operating System` | Task delegation | `tools.configuration set-os` | OS config update |
| 2 | `Setup 2: Install Python Virtual Environment` | Task delegation | `preLaunchTask` | `.venv` creation, dependency installation |
| 3 | `Setup 3: Install Ollama and Local LLM` | Task delegation | `preLaunchTask` | Ollama installation, selected model pull |
| 4 | `Check 1: Refresh Environment Check File` | Task delegation | `preLaunchTask` | Environment check |
| 5 | `Run 3: Extension Module` | `.venv` Python | `tools.extension_runner` | Future module execution |
| 6 | `Test Result: Generate Latest Markdown` | `.venv` Python | `test_result --docs` | Latest result analysis, Markdown generation |
| 7 | `Debug: Current Python File` | `.venv` Python | Current file | Application/tool debugging |
| 8 | `Debug: Current pytest File` | `.venv` Python | pytest current file | Test debugging |

| Launch constraint | Value |
|---|---|
| Setup entry | Task delegation |
| Check entry | Task delegation |
| Background process | None |
| Setup location | `.vscode/tasks.json` |

| Setup 1 runtime | Rule |
|---|---|
| Launch Python | `python` |
| Task Python | `python` |
| `sys.prefix == sys.base_prefix` | Continue |
| `sys.prefix != sys.base_prefix` | System Python `execv` |
| System executable | `sys._base_executable` |

| Setup input | Options | Default | Validation |
|---|---|---|---|
| `targetOS` | `auto`, `windows`, `linux`, `macos` | `auto` | Stored in `config/config.json` |

| VS Code Python path | Value |
|---|---|
| Setup 1·2 | `python` |
| Setup 3+ | `${config:python.defaultInterpreterPath}` |
| OS-specific path | `.vscode/settings.json` only |
| Testing interpreter sync | Setup 1 → `.vscode/settings.json` |

### 3.1 Python Environment Setup

```text
System Python
    │
    ▼
python -m venv .venv
    │
    ▼
.venv Python
    │
    ├── ensurepip
    ├── pip upgrade
    └── requirements.txt install
```

### 3.2 Ollama and Local LLM Setup

```text
Ollama executable check
├── Found
│   └── Server health check
└── Not found
    ├── Windows: winget
    ├── macOS: Homebrew
    └── Linux: official installer
          │
          ▼
Foreground Ollama server check
          │
          ├── Ready: ollama pull <selected-model>
          └── Not ready: setup stop
```

| Server state before setup | Setup behavior | Server state after setup |
|---|---|---|
| Running | Reuse | Running; external ownership |
| Stopped | Setup stop | Stopped |
| Remote endpoint | Health check only | Unchanged |

| Platform | Installer | Requirement |
|---|---|---|
| Windows | `winget install Ollama.Ollama` | `winget` |
| Linux | `https://ollama.com/install.sh` | `sh` |
| macOS | `brew install ollama` | Homebrew |

### 3.3 Extension Module Contract

```python
def main() -> int | None:
    ...
```

```text
tools.extension_runner
    │
    ├── --module <python.module>
    ├── import module
    ├── find main()
    └── execute main()
```

## 4. VS Code Testing

Source: `.vscode/settings.json`

| Setting | Value |
|---|---|
| Interpreter | `${workspaceFolder}/.venv` |
| Adapter | pytest |
| pytest path 1 | `tests/pytest` |
| pytest path 2 | `tests/unittest` |
| unittest implementation | Standard `unittest.TestCase` |
| Separate unittest execution | `TEST 3: Run unittest Suite` task |
| VS Code pytest cache | `-p no:cacheprovider` |

```text
VS Code Testing
└── pytest adapter
    ├── tests/pytest
    │   └── Integration / Functional / Hardware CT
    └── tests/unittest
        └── Standard unittest.TestCase
```

Constraint:

- VS Code Python extension: single active test adapter
- Selected adapter: pytest
- unittest compatibility: pytest discovery + native unittest task

## 5. VS Code Tasks

Source: `.vscode/tasks.json`

| Group | Task |
|---|---|
| Setup | `Setup 1: Select Operating System` |
| Setup | `Setup 2: Install Python Virtual Environment` |
| Setup | `Setup 3: Install Ollama and Local LLM` |
| Check | `Check: Refresh Environment Check File` |
| Runtime | `Local LLM: Run Ollama Server (Foreground)` |
| TEST 1 | `TEST 1: Run All with pytest` |
| TEST 2 | `TEST 2: Run Continuous Tests` |
| TEST 3 | `TEST 3: Run unittest Suite` |
| Report | `Report: Generate Latest Markdown` |
| Report | `Report: Convert Latest Markdown to HTML` |
| MkDocs | `MkDocs: Serve Locally` |
| MkDocs | `MkDocs: Serve on Network` |
| MkDocs | `MkDocs: Build` |
| MkDocs | `MkDocs: Build Strict` |

| Task runtime | Command |
|---|---|
| Python / Test / Report | `${config:python.defaultInterpreterPath}` |
| MkDocs | `${config:python.defaultInterpreterPath} -m mkdocs` |
| Platform-specific activation script | None |

## 6. Test Architecture

| Interface | Mock | CT ID | Category |
|---|---|---|---|
| UART | `MockUARTInterface` | `CT-UART-001` | timing |
| USB | `MockUSBInterface` | `CT-USB-001` | communication |
| Network | `MockNetworkInterface` | `CT-NETWORK-001` | communication |

```text
tests/
├── pytest/
│   ├── test_cases/
│   │   ├── communication/
│   │   ├── timing/
│   │   ├── functional/
│   │   ├── performance/
│   │   ├── stability/
│   │   └── regression/
│   ├── test_equipments/
│   │   ├── fpga/
│   │   ├── saleae/
│   │   └── digilent/
│   ├── test_interfaces/
│   │   ├── usb/
│   │   ├── uart/
│   │   ├── jtag/
│   │   └── network/
│   └── conftest.py
└── unittest/
    ├── python/
    ├── c_cpp/
    ├── firmware/
    └── common/
```

### 6.1 Test Scope

| Directory | Scope |
|---|---|
| `tests/pytest` | Integration, functional, hardware, interface, regression |
| `tests/unittest/python` | Python function, class, module, mock |
| `tests/unittest/c_cpp` | C/C++ unit test extension |
| `tests/unittest/firmware` | Firmware unit test extension |
| `tests/unittest/common` | Shared unit-test assets |

### 6.2 Equipment and Interface Separation

| Layer | Meaning | Examples |
|---|---|---|
| Test Equipment | Measurement/control device | FPGA, Saleae, Digilent |
| Test Interface | DUT communication transport | USB, UART, JTAG, Network |
| Test Case | Scenario and assertions | Timing, throughput, stability |

```text
pytest Test Case
├── Test Interface ──► DUT
└── Test Equipment ──► DUT
```

### 6.3 Interface Contract

```python
connect()
disconnect()
read()
write()
execute()
```

## 7. Test Execution Data

```text
Test Execution
├── Result
│   ├── Test ID
│   ├── PASS / FAIL / ERROR / SKIP
│   ├── Duration
│   ├── Environment
│   ├── Configuration
│   └── Commit
├── Log
│   ├── test.log
│   ├── stdout.log
│   ├── stderr.log
│   ├── equipment.log
│   └── interface.log
└── Measurement
    ├── measurement.json
    └── measurement.csv
```

## 8. Test Result Generation

Entry point: `python -m test_result`

Input rule:

```text
reports/logs/*/*/result.json
              │
              ▼
Maximum execution ID
              │
              ▼
Latest result
```

Execution rule:

- Test re-execution: prohibited
- Input: newest `result.json`
- Logs: same execution directory
- Analysis: Local LLM or deterministic fallback
- Canonical output: execution-specific Markdown
- Latest output: fixed latest Markdown path
- Optional MkDocs latest copy: `--docs`
- MkDocs execution snapshot: append-only
- Previous canonical reports: snapshot backfill
- MkDocs system index: manual
- MkDocs pytest result index: automatic regeneration
- MkDocs unittest result index: automatic regeneration
- MkDocs navigation: manual `mkdocs.yml` configuration
- Optional source review: `--source-review`

```text
Latest result.json
      +
Latest execution logs
      │
      ▼
Local LLM Analysis
      │
      ▼
reports/markdown/<test-id>/<execution-id>/result.md
      │
      ├── reports/markdown/<test-id>/latest.md
      ├── test_result/markdown/latest.md
      └── docs/test/...  [--docs]
          ├── <test-id>.md                    # Latest
          └── <test-id>/<execution-id>.md     # Per execution
      │
      ├── docs/pytest_results.md              # Auto-generated pytest catalog
      └── docs/unittest_results.md            # Auto-generated unittest catalog
```

## 9. Markdown Report Schema

```text
# <Test ID> Test Result
├── Test summary
├── Measurement
├── Statistics
├── Important logs
├── Warnings
├── Local LLM analysis
│   ├── Classification
│   ├── Confidence
│   ├── Failure analysis
│   └── Source review
└── Test history
```

## 10. Local LLM Analysis

| Component | Value |
|---|---|
| Runtime | Ollama |
| Default endpoint | `http://127.0.0.1:11434` |
| Environment variable | `OLLAMA_URL` |
| Configured model | `config/config.json` → `ollama.selected_model` |
| Model variable | `OLLAMA_MODEL` |
| Project config | `config/config.json` |
| Environment check | `config/check.json` |
| Selection priority | CLI → Environment → Config |
| Missing model | Configuration error |
| Config selection | `ollama.selected_model` |
| Installed inventory | Ollama `/api/tags` |
| Offline fallback | Deterministic analysis |

| Process | Execution mode | Stop rule |
|---|---|---|
| Setup task | No child server | Task completion |
| Existing Ollama server | External process | No control |
| VS Code Ollama server task | Foreground process task | VS Code task termination |

Model config schema:

```text
config/config.json
├── version
├── os
└── ollama
    ├── url
    └── selected_model
```

Environment check schema:

```text
config/check.json
├── generated_at
├── os
│   ├── configured
│   ├── detected
│   └── name
├── python
│   ├── installed
│   ├── executable
│   └── version
└── ollama
    ├── installed
    ├── executable
    ├── version
    ├── available
    ├── endpoint
    ├── selected_model
    ├── selected_model_installed
    └── supported_models
```

Runtime status schema:

```text
Local LLM Status
├── endpoint
├── configured_model
├── configured_model_installed
├── available
└── installed_models
    ├── name
    ├── size
    ├── modified_at
    └── digest
```

Analysis outputs:

- Test summary
- Failure classification
- Confidence
- Warning severity
- Failure analysis
- Source review
- Codex escalation flag

Warning severity:

- Critical
- Important
- Low

## 11. Codex Escalation

Trigger conditions:

- Local LLM confidence `< 0.5`
- Local LLM inconclusive result
- Unknown root cause
- Repeated failure
- Multi-file modification
- Refactoring
- Architecture change
- Explicit source fix request

```text
Local LLM
├── Resolved ──► Complete
└── Escalation required ──► Codex
```

## 12. Documentation Outputs

| Output | Source | Destination |
|---|---|---|
| Canonical Markdown | Latest test execution | `reports/markdown/<test-id>/<execution-id>/result.md` |
| Per-test latest Markdown | Canonical Markdown | `reports/markdown/<test-id>/latest.md` |
| Global latest Markdown | Canonical Markdown | `test_result/markdown/latest.md` |
| MkDocs latest page | Canonical Markdown | `docs/test/.../<test-id>.md` |
| MkDocs execution page | Canonical Markdown | `docs/test/.../<test-id>/<execution-id>.md` |
| MkDocs system index | System architecture | `docs/index.md` |
| MkDocs pytest result index | Published CT page scan | `docs/pytest_results.md` |
| MkDocs unittest result index | Published unit page scan | `docs/unittest_results.md` |
| DOCX | Canonical Markdown | Pandoc output |
| PDF | Canonical Markdown | Pandoc output |
| HTML | Canonical Markdown | Pandoc output |

## 13. GitHub Automation

```text
GitHub Actions
├── GitHub-hosted Runner
│   ├── Unit Test
│   ├── Mock CT
│   ├── Result Analysis
│   └── Markdown Generation
└── Self-hosted Runner [Optional]
    ├── USB / JTAG
    ├── Vendor Tool
    ├── Internal Network
    ├── Hardware Equipment
    └── Machine-specific Environment
```

GitHub Issue content:

- Test configuration
- PASS / FAIL
- Measurement summary
- Warning summary
- Local LLM summary
- Markdown path
- MkDocs path
- Artifact path

Excluded from GitHub Issue:

- Full raw log
- Full measurement data
- Complete stack trace dump

## 14. Repository Structure

```text
.
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── config/
│   ├── config.json                # Selected OS and Ollama model
│   └── check.json                 # Generated environment check
├── .venv/                         # Git ignored
├── tests/
│   ├── pytest/
│   └── unittest/
├── test_result/
│   ├── __init__.py
│   ├── __main__.py
│   └── markdown/
│       └── latest.md              # Generated, Git ignored
├── tools/
│   ├── configuration/
│   ├── local_llm/
│   ├── extensions/
│   ├── github_reporter/
│   ├── log_parser/
│   ├── mkdocs_reporter/
│   ├── pandoc_reporter/
│   ├── result_normalizer/
│   ├── environment_setup.py
│   ├── extension_runner.py
│   └── pipeline.py
├── reports/
│   ├── logs/
│   ├── measurements/
│   └── markdown/
├── docs/
│   ├── index.md                     # Manual system overview
│   ├── pytest.md                    # pytest system description
│   ├── unittest.md                  # unittest system description
│   ├── pytest_results.md            # Auto-generated pytest catalog
│   ├── unittest_results.md          # Auto-generated unittest catalog
│   └── test/                        # Latest and execution reports
├── DESIGN.md
├── mkdocs.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

## 15. Final Workflow

```text
Tasks: Environment Setup
              │
              ▼
            .venv
              │
              ▼
VS Code Testing
├── tests/pytest
└── tests/unittest
              │
              ▼
Result + Log + Measurement + Warning
              │
              ▼
test_result: Latest Result Selection
              │
              ▼
Ollama + Local LLM
              │
              ▼
Markdown
├── Latest Report
├── MkDocs
├── Pandoc
└── GitHub Issue
              │
              ▼
Codex [Escalation Only]
```
