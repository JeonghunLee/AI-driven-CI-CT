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
│   ├── test_envs/tests/pytest
│   └── test_envs/tests/unittest
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
├── test_envs/reports/markdown
├── test_envs/reports/pandoc
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
| 1 | `SETUP 1: Select Operating System` | Task delegation | `test_envs.tools.configuration select-os` | OS config update |
| 2 | `SETUP 2: Install Python Virtual Environment` | Task delegation | `preLaunchTask` | `.venv` creation, dependency installation |
| 3 | `SETUP 3: Install Ollama and Local LLM` | Task delegation | `preLaunchTask` | Ollama installation, selected model pull |
| 4 | `CHECK 1: Refresh Environment Check File` | Task delegation | `preLaunchTask` | Environment check |
| 5 | `Run 3: Extension Module` | `.venv` Python | `test_envs.tools.extension_runner` | Future module execution |
| 6 | `Test Result: Generate Pending Markdown` | `.venv` Python | `test_envs.tools.test_result --pending --docs` | Missing Execution ID analysis, Markdown generation |

| Pending progress | Format |
|---|---|
| Running | `[current/total] RUNNING <seconds>s <TEST-ID> / <Execution-ID>` |
| Complete | `[current/total] COMPLETE <seconds>s <TEST-ID> / <Execution-ID>` |
| Error | `[current/total] ERROR <seconds>s <TEST-ID> / <Execution-ID>` |
| Interval | `1 second` |
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
| `targetOS` | `auto`, `windows`, `linux`, `macos` | `auto` | Stored in `test_envs/configs/config.json` |

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
test_envs.tools.extension_runner
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
| pytest path 1 | `test_envs/tests/pytest` |
| pytest path 2 | `test_envs/tests/unittest` |
| unittest implementation | Standard `unittest.TestCase` |
| unittest execution | VS Code Testing / pytest |
| VS Code pytest cache | `-p no:cacheprovider` |

```text
VS Code Testing
└── pytest adapter
    ├── test_envs/tests/pytest
    │   └── Integration / Functional / Hardware CT
    └── test_envs/tests/unittest
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
| SETUP | `SETUP 1: Select Operating System` |
| SETUP | `SETUP 2: Install Python Virtual Environment` |
| SETUP | `SETUP 3: Install Ollama and Local LLM` |
| CHECK | `CHECK 1: Refresh Environment Check File` |
| CHECK | `CHECK 2: Show Environment Configuration` |
| CHECK | `CHECK 3: Run Ollama Server (Foreground)` |
| TEST CASE | `TEST CASE: ALL` |
| TEST CASE | `TEST CASE: TEST ID` / marker ID picker |
| REPORT | `REPORT: Generate Pending Markdown` |
| REPORT | `REPORT: Convert Latest Markdown to HTML` |
| REPORT | `REPORT: Convert Latest Markdown to DOCX` |
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

| Test case registration | Value |
|---|---|
| Source | `@pytest.mark.ct` |
| Required fields | `test_id`, `category`, `fixture_id`, `fixture_mode` |
| Optional field | `test_prompt` |
| Interface / Equipment owner | Fixture `FIXTURE_META` |
| Mode support owner | Fixture `FIXTURE_META.modes` |
| Mapping validation | Filename + Fixture ID + fixture argument |
| Collection validation | Required fields + unique TEST ID + filename/fixture ID + fixture mode |
| Missing field / duplicate ID | pytest collection error |

| Tool implementation | Path | IDs |
|---|---|---|
| Equipment | `test_envs/tests/pytest/test_equipments/` | `fpga`, `saleae`, `digilent` |
| Interface | `test_envs/tests/pytest/test_interfaces/` | `uart`, `usb`, `jtag`, `network` |

| Mode | Tool path | Result field |
|---|---|---|
| Mock | `<tool>/mock/` | `mock` |
| HIL | `<tool>/hil/` | `hil` |
| No equipment | None | `none` |

| Selection | Derived result fields |
|---|---|
| `@pytest.mark.ct:fixture_mode` | `test_mode`, `interface_mode`, `equipment_mode` |

```text
test_envs/tests/
├── pytest/
│   ├── test_cases/
│   │   ├── test_fixture_001_uart_timing.py
│   │   ├── test_fixture_002_usb_loopback.py
│   │   └── test_fixture_003_network_loopback.py
│   ├── fixtures/
│   │   ├── fixture_001_uart_saleae.py
│   │   ├── fixture_002_usb_digilent.py
│   │   ├── fixture_003_network.py
│   │   ├── fixture_004_jtag_fpga.py
│   │   └── fixture_005_full_hil.py
│   ├── test_equipments/
│   │   ├── fpga/{mock,hil}/
│   │   ├── saleae/{mock,hil}/
│   │   └── digilent/{mock,hil}/
│   ├── test_interfaces/
│   │   ├── usb/{mock,hil}/
│   │   ├── uart/{mock,hil}/
│   │   ├── jtag/{mock,hil}/
│   │   └── network/{mock,hil}/
│   └── conftest.py
└── unittest/
    ├──ct_framework
    │      └──python/
    ├── python/    
    ├── c_cpp/
    ├── firmware/
    └── common/
```

### 6.1 Test Scope

| Directory | Scope |
|---|---|
| `test_envs/tests/pytest` | Integration, functional, hardware, interface, regression |
| `test_envs/tests/unittest/ct_framework/python` | CT framework unit tests |
| `test_envs/tests/unittest/python` | Product Python unit-test extension |
| `test_envs/tests/unittest/c_cpp` | C/C++ unit-test extension |
| `test_envs/tests/unittest/firmware` | Firmware unit-test extension |
| `test_envs/tests/unittest/common` | Shared unit-test assets |

### 6.2 Fixture-to-Test Mapping

| Order | Fixture composition | Test case | TEST ID |
|---:|---|---|---|
| 1 | `fixture_001_uart_saleae.py` | `test_fixture_001_uart_timing.py` | `CT-UART-001` |
| 2 | `fixture_002_usb_digilent.py` | `test_fixture_002_usb_loopback.py` | `CT-USB-001` |
| 3 | `fixture_003_network.py` | `test_fixture_003_network_loopback.py` | `CT-NETWORK-001` |

| Fixture mode source | Priority |
|---|---:|
| CLI `--fixture-mode=mock|hil` | 1 |
| Marker `fixture_mode` | 2 |

### 6.3 Equipment and Interface Separation

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

### 6.4 Interface Contract

```python
connect()
disconnect()
read()
write()
execute()
```

## 7. Test Execution Data

### 7.1 Identifier Definitions

| Identifier | Scope | Definition | Purpose | Format | Example |
|---|---|---|---|---|---|
| TEST ID | pytest only | `test_envs/tests/pytest/test_cases` definition | Test case identification | `CT-<TARGET>-<NNN>` | `CT-NETWORK-001` |
| Execution ID | pytest, unittest | Execution result generation | Result delimiter | `YYYYMMDD_HHMMSS_ffffff` | `20260819_094832_960333` |

| Runner | Primary key | TEST ID |
|---|---|---|
| pytest | `TEST ID + Execution ID` | Required |
| unittest | `Execution ID` | Prohibited |

| Artifact | Identifier rule | Search rule |
|---|---|---|
| Result JSON | Execution ID creation source | Execution ID |
| Test log | Source Execution ID reuse | Execution ID |
| Local LLM log | Source Execution ID reuse | Execution ID |
| Markdown | Source Execution ID reuse | Execution ID |
| Pandoc | Source Execution ID reuse | Execution ID |

```text
Execution ID
├── Result JSON
├── Test log
├── Local LLM log
├── Markdown
└── Pandoc
```

```text
Execution ID
├── YYYYMMDD       # Asia/Seoul date
├── HHMMSS         # Asia/Seoul time
└── ffffff         # Microseconds
```

| Time field | Config source | Rule |
|---|---|---|
| Timezone name | `test_envs/configs/config.json` → `time.timezone` | `Asia/Seoul` |
| UTC offset | `test_envs/configs/config.json` → `time.utc_offset_hours` | SeoulTime correction |
| Date·Time | `configured_now()` | Config value required |

### 7.2 Execution Artifacts

```text
Test Execution
├── <execution-id>_result.json
│   ├── test_case
│   ├── test_configs
│   ├── fixture_configs
│   ├── test_src
│   ├── test_result
│   └── test_analysis
└── <execution-id>_test.log
    ├── Test
    ├── Stdout
    ├── Stderr
    ├── Equipment
    └── Interface
```

## 8. Test Result Generation

Entry point: `python -m test_envs.tools.test_result`

Input rule:

```text
pytest   : test_envs/reports/results/pytest/test_cases/<test-id>/<execution-id>_result.json
unittest : test_envs/reports/results/unittest/<execution-id>_result.json
           test_envs/reports/results/unittest/<execution-id>_result.log
```

Execution rule:

- Test re-execution: prohibited
- Input: newest `<execution-id>_result.json`
- Pending input: Execution ID without Markdown or MkDocs document
- Logs: same Execution ID location
- Analysis: Local LLM or deterministic fallback
- Canonical output: execution-specific Markdown
- Duplicate latest output: none
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
pytest   : test_envs/reports/markdown/<test-id>/<execution-id>_result.md
unittest : test_envs/reports/markdown/unittest/<execution-id>_result.md
      │
      ├── test_envs/reports/pandoc/<test-id>/<execution-id>_result.<format>
      ├── docs/tests/pytest/  [--docs]
      │   ├── <test-id>.md
      │   └── <test-id>__<execution-id>.md
      └── docs/tests/unittest/  [--docs]
          └── <execution-id>.md
      │
      ├── docs/tests/pytest/index.md           # Auto-generated pytest index
      └── docs/tests/unittest/index.md         # Auto-generated unittest index
```

## 9. Markdown Report Schema

```text
# <Test ID> Test Result
├── Test summary
│   ├── Test configs
│   │   ├── Test Item table
│   │   │   ├── Test ID
│   │   │   ├── Category
│   │   │   ├── Fixture ID
│   │   │   └── Fixture mode
│   │   └── Fixture table
│   │       ├── Interface
│   │       ├── Equipment
│   │       ├── Equipment mode
│   │       └── Interface mode
│   ├── Test Source
│   ├── Measurement
│   ├── Statistics
│   └── Logs
└── Local LLM Analysis
    ├── Classification
    ├── Confidence
    ├── Analyzer
    ├── Status
    ├── LLM Test Prompt
    ├── Test Result
    │   ├── Status
    │   ├── Severity
    │   ├── Warnings
    │   └── Needs Escalation
    └── Test Summary
        ├── Summary
        ├── Failure Analysis
        ├── Source Review
        ├── Warnings
        └── Recommendations
```

| Index field | Source |
|---|---|
| Category | Latest `result.json` → `test_case.category` |
| Mode | Latest `result.json` → `fixture_configs.test_mode` |
| Test ID | Latest TEST document link |
| Latest | Latest `result.json` → Seoul timestamp date |
| Execution Count | `docs/tests/pytest/<test-id>__<execution-id>.md` count |

| Recent Executions column | Source |
|---|---|
| Execution ID | Execution document link |
| Category | Matching `result.json` → `test_case.category` |
| Test ID | pytest TEST ID |

| unittest index column | Source |
|---|---|
| Test Function Count | Latest unittest `summary.total` |
| Pass | Latest unittest Execution status |
| Latest | Latest unittest Seoul timestamp date + Execution document link |

| unittest Recent Executions column | Source |
|---|---|
| Execution ID | Execution document link |
| Result | Execution status |
| Tests | `summary.total` |
| Passed | `summary.passed` |
| Failed | `summary.failed + summary.errors` |

| unittest excluded field | Rule |
|---|---|
| Test ID | pytest only |
| Mode | pytest only |

### unittest Result Contract

| Field | Rule |
|---|---|
| TEST ID | Not serialized |
| Mode | Not serialized |
| Identifier | Execution ID |
| `test_functions[].function` | Test Function name |
| `test_functions[].path` | Test source file path; Markdown PATH uses parent directory |
| `test_functions[].pass` | Boolean pass result |
| `test_functions[].status` | `PASS`, `FAIL`, `ERROR`, `SKIP` |
| `test_functions[].failure` | Failure detail |

```text
execution
summary
test_functions[]
```

| unittest Local LLM | Rule |
|---|---|
| Analysis | Not used |
| Ollama request | Not used |
| Local LLM log | Not generated |

## 10. Local LLM Analysis

| Component | Value |
|---|---|
| Runtime | Ollama |
| Default endpoint | `http://127.0.0.1:11434` |
| Environment variable | `OLLAMA_URL` |
| Configured model | `test_envs/configs/config.json` → `ollama.selected_model` |
| Model variable | `OLLAMA_MODEL` |
| Project config | `test_envs/configs/config.json` |
| Environment check | `test_envs/configs/check.json` |
| Selection priority | CLI → Environment → Config |
| Missing model | Configuration error |
| Config selection | `ollama.selected_model` |
| Installed inventory | Ollama `/api/tags` |
| Offline fallback | Deterministic analysis |
| Default prompt | `ollama.default_prompt` |
| TEST prompt | `@pytest.mark.ct(test_prompt="...")` |
| Prompt priority | Non-empty `test_prompt` → `default_prompt` |
| Timeout | `ollama.max_timeout_s` |
| Retry | `ollama.max_retry` |
| Diagnostic log | `test_envs/reports/local_llm/<execution-id>_local_llm.log` |
| Markdown input | `result.json`, `test.log` only |

| Process | Execution mode | Stop rule |
|---|---|---|
| Setup task | No child server | Task completion |
| Existing Ollama server | External process | No control |
| VS Code Ollama server task | Foreground process task | VS Code task termination |
| VS Code task + existing server | Endpoint reuse | Exit `0` |

Model config schema:

```text
test_envs/configs/config.json
├── version
├── os
├── time
│   ├── timezone
│   └── utc_offset_hours
└── ollama
    ├── url
    ├── selected_model
    ├── default_prompt
    ├── max_timeout_s
    └── max_retry
```

Environment check schema:

```text
test_envs/configs/check.json
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

| Warning count | Severity |
|---:|---|
| 0–1 | `LOW` |
| 2–3 | `MEDIUM` |
| 4–5 | `HIGH` |
| 6+ | `CRITICAL` |

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
| pytest Canonical Markdown | pytest execution | `test_envs/reports/markdown/<test-id>/<execution-id>_result.md` |
| unittest Canonical Markdown | unittest execution | `test_envs/reports/markdown/unittest/<execution-id>_result.md` |
| Duplicate latest Markdown | None | None |
| MkDocs pytest latest page | Canonical Markdown | `docs/tests/pytest/<test-id>.md` |
| MkDocs unittest execution page | Canonical Markdown | `docs/tests/unittest/<execution-id>.md` |
| pytest MkDocs execution | Canonical Markdown | `docs/tests/pytest/<test-id>__<execution-id>.md` |
| unittest MkDocs execution | Canonical Markdown | `docs/tests/unittest/<execution-id>.md` |
| Latest page history | Normalized TEST results | Date + Time + linked Execution ID + 7-character commit |
| Execution page history | None | None |
| MkDocs index | Document links·system summary | `docs/index.md` |
| Python environment document | OS·Python·venv | `docs/python_environment.md` |
| Local LLM environment document | Ollama·model·prompt | `docs/local_llm_environment.md` |
| VS Code environment document | Settings·Testing·Discovery·Launch·Tasks | `docs/vscode_environment.md` |
| Pytest operation document | TEST ID·Fixture·Local LLM·Report | `docs/pytest_operation.md` |
| Unittest operation document | Function·Execution ID·Result·Report | `docs/unittest_operation.md` |
| pytest framework document | Test cases·fixtures·HIL·Mock·CLI override·HIL gate | `docs/pytest_framework.md` |
| MkDocs pytest result index | Published pytest page scan | `docs/tests/pytest/index.md` |
| MkDocs unittest result index | Published unittest page scan | `docs/tests/unittest/index.md` |
| DOCX | Canonical Markdown | `test_envs/reports/pandoc/<test-id>/<execution-id>_result.docx` |
| PDF | Canonical Markdown | `test_envs/reports/pandoc/<test-id>/<execution-id>_result.pdf` |
| HTML | Canonical Markdown | `test_envs/reports/pandoc/<test-id>/<execution-id>_result.html` |

## 13. GitHub Automation

<br/>

```text
test_check.yml Issue
        |
        v
continuous-test.yml --> selected runner --> automatic environment detection
                                                |
                                                v
                                       github_reporter --> Issue comment

pytest_request.yml or unittest_request.yml Issue
        |
        v
continuous-test.yml: request job
        |
        v
test_envs.tools.issue_parser
        |
        +-- GitHub-hosted Linux ---> ubuntu-latest
        +-- GitHub-hosted Windows --> windows-latest
        +-- Self-hosted HIL Linux --> [self-hosted, linux, hw-test]
        +-- Self-hosted HIL Windows -> [self-hosted, windows, hw-test]
        |
        v
continuous-test.yml: test job
        |
        +-- Pytest ------> TEST ID + marker/mock/hil --> Local LLM
        |
        +-- Unittest ----> Unittest scope ----------> No Local LLM
        |
        v
Explicit normalized result
        |
        v
test_envs.tools.pipeline
        |
        +-- mkdocs_reporter ------> MkDocs Markdown
        +-- pandoc_reporter ------> HTML / DOCX
        +-- github_reporter ------> Request Issue comment
        +-- upload-artifact ------> Test evidence / Coverage
```

<br/>

| Automation item | Design rule |
|---|---|
| Pytest request | `.github/ISSUE_TEMPLATE/pytest_request.yml`; TEST ID and Fixture mode are present only here |
| Unittest request | `.github/ISSUE_TEMPLATE/unittest_request.yml`; Unittest scope is present only here |
| Environment check request | `.github/ISSUE_TEMPLATE/test_check.yml`; user selects only the runner |
| Environment check result | Workflow detects host type, OS, Python, and Ollama and posts them through `github_reporter` |
| Unified workflow | `.github/workflows/continuous-test.yml` (`Test Request`) |
| Automatic trigger | Request Issue opened, edited, or reopened |
| Label provisioning | A relevant default-branch push creates both labels; the request job also recognizes `[PYTEST-REQUEST]`, `[UNITTEST-REQUEST]`, and `[TEST-CHECK]` |
| Rerun trigger | Edit or reopen the Issue, or use manual `workflow_dispatch` |
| Local/manual trigger | `workflow_dispatch`; replaces the former local request workflow |
| Default runner | GitHub-hosted Linux (`ubuntu-latest`) |
| Hosted compatibility | Mock CT and Unittest run on GitHub-hosted Linux or Windows |
| HIL Linux | `[self-hosted, linux, hw-test]` |
| HIL Windows | `[self-hosted, windows, hw-test]` |
| HIL constraint | Physical equipment requires a matching Self-hosted OS runner and never falls back to Mock |
| Pytest selection | `CT-UART-001`, `CT-USB-001`, or `CT-NETWORK-001` plus `marker`, `mock`, or `hil` Fixture mode |
| Unittest selection | All Unittest, CT Framework Python, or one path/node ID below `test_envs/tests/unittest` |
| Coverage | None, terminal missing-lines, or HTML report |
| Result selection | Only the normalized result created after the current workflow marker |
| Issue-form report selection | Optional Pandoc HTML/DOCX; canonical Markdown remains part of the common pipeline |
| Failure handling | Test failures keep the normalized result; setup/capture failures post an ERROR comment |

The previous separate HIL responsibility is handled by dynamic runner selection. Local/manual requests are handled by `workflow_dispatch` inputs in the same unified workflow.

<br/>

GitHub Issue content:

- Test configuration
- PASS / FAIL
- Measurement summary
- Warning summary
- Pytest Local LLM summary, or `Not used` for Unittest
- Markdown path
- MkDocs path
- Artifact path

Excluded from GitHub Issue:

- Full raw log
- Full measurement data
- Complete stack trace dump

<br/>

## 14. Repository Structure

<br/>

| GitHub automation source | Role |
|---|---|
| `.github/ISSUE_TEMPLATE/pytest_request.yml` | Pytest-only request form |
| `.github/ISSUE_TEMPLATE/unittest_request.yml` | Unittest-only request form |
| `.github/ISSUE_TEMPLATE/test_check.yml` | Runner-only request for automatic host type, OS, Python, and Ollama detection |
| `.github/workflows/continuous-test.yml` | Unified request parsing, runner routing, test, report, Issue update, and artifact workflow |
| `test_envs/tools/issue_parser.py` | Issue Form and manual input normalization |
| `test_envs/tools/github_reporter/` | Result and workflow-error Issue comments |

```text
.
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── pytest_request.yml
│   │   ├── unittest_request.yml
│   │   └── test_check.yml
│   └── workflows/
│       ├── continuous-test.yml
│       └── github_pages.yaml
├── .venv/                         # Git ignored
├── docs/
│   ├── index.md                     # Manual system overview
│   ├── python_environment.md        # Python environment
│   ├── local_llm_environment.md     # Local LLM environment
│   ├── vscode_environment.md        # VS Code environment
│   ├── pytest_operation.md          # Pytest operation
│   ├── unittest_operation.md        # Unittest operation
│   ├── pytest_framework.md          # pytest system, HIL, and Mock
│   ├── unittest_framework.md        # unittest system description
│   └── tests/
│       ├── pytest/                  # Markdown only
│       └── unittest/                # Markdown only
├── test_envs/
│   ├── configs/
│   │   ├── config.json
│   │   └── check.json
│   ├── tests/
│   │   ├── pytest/
│   │   └── unittest/
│   │       ├── ct_framework/python/
│   │       ├── python/
│   │       ├── c_cpp/
│   │       ├── firmware/
│   │       └── common/
│   ├── reports/
│   │   ├── results/pytest/test_cases/<test-id>/
│   │   ├── results/unittest/<execution-id>_result.json
│   │   ├── pandoc/<test-id>/
│   │   └── markdown/<test-id>/
│   └── tools/
│       ├── configuration/
│       ├── local_llm/
│       ├── mkdocs_reporter/
│       ├── pandoc_reporter/
│       ├── result_normalizer/
│       ├── test_result/
│       ├── environment_setup.py
│       └── pipeline.py
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
├── test_envs/tests/pytest
└── test_envs/tests/unittest
              │
              ▼
Result + Log + Measurement + Warning
              │
              ▼
test_envs.tools.test_result: Latest Result Selection
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
