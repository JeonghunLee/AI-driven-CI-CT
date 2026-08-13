# AI-driven Continuous Testing Architecture

## 1. Core Principles

| Item | Definition |
|---|---|
| Development front-end | VS Code |
| Python runtime | Project-local `.venv` |
| Unit test | `unittest` |
| Continuous test | `pytest` |
| Local LLM runtime | Ollama |
| Primary model | `deepseek-r1:7b` |
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
│   ├── Python .venv Setup
│   ├── Ollama + DeepSeek Setup
│   ├── Extension Module
│   └── Latest Markdown Report
├── Testing
│   ├── tests/pytest
│   └── tests/unittest
└── Tasks
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
Ollama + DeepSeek
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
| 1 | `Setup 1: Install Python Virtual Environment` | System Python | `tools.environment_setup python` | `.venv` creation, dependency installation |
| 2 | `Setup 2: Install Ollama and DeepSeek` | `.venv` Python | `tools.environment_setup ollama` | Ollama installation, server startup, DeepSeek pull |
| 3 | `Run 3: Extension Module` | `.venv` Python | `tools.extension_runner` | Future module execution |
| 4 | `Test Result: Generate Latest Markdown` | `.venv` Python | `test_result --docs` | Latest result analysis, Markdown generation |
| 5 | `Debug: Current Python File` | `.venv` Python | Current file | Application/tool debugging |
| 6 | `Debug: Current pytest File` | `.venv` Python | pytest current file | Test debugging |

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

### 3.2 Ollama and DeepSeek Setup

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
Ollama server startup
          │
          ▼
ollama pull deepseek-r1:7b
```

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
| Interpreter | `${workspaceFolder}\.venv\Scripts\python.exe` |
| Adapter | pytest |
| pytest path 1 | `tests/pytest` |
| pytest path 2 | `tests/unittest` |
| unittest implementation | Standard `unittest.TestCase` |
| Separate unittest execution | `Test: Run unittest Suite` task |

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
| Setup | `Setup: Create Python Virtual Environment` |
| Setup | `Setup: Install Ollama and Pull DeepSeek` |
| Test | `Test: Run All with pytest` |
| Test | `Test: Run Continuous Tests` |
| Test | `Test: Run unittest Suite` |
| Report | `Report: Generate Latest Markdown` |
| Report | `Report: Convert Latest Markdown to HTML` |
| MkDocs | `MkDocs: Serve Locally` |
| MkDocs | `MkDocs: Serve on Network` |
| MkDocs | `MkDocs: Build` |
| MkDocs | `MkDocs: Build Strict` |
| Build | `Package Electron` |

## 6. Test Architecture

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
- Analysis: DeepSeek or deterministic fallback
- Canonical output: execution-specific Markdown
- Latest output: fixed latest Markdown path
- Optional MkDocs latest copy: `--docs`
- MkDocs execution snapshot: append-only
- Previous canonical reports: snapshot backfill
- Optional source review: `--source-review`

```text
Latest result.json
      +
Latest execution logs
      │
      ▼
DeepSeek Analysis
      │
      ▼
reports/markdown/<test-id>/<execution-id>/result.md
      │
      ├── reports/markdown/<test-id>/latest.md
      ├── test_result/markdown/latest.md
      └── docs/test/...  [--docs]
          ├── <test-id>.md                    # Latest
          └── <test-id>/<execution-id>.md     # Per execution
```

## 9. Markdown Report Schema

```text
# <Test ID> Test Result
├── Test summary
├── Measurement
├── Statistics
├── Important logs
├── Warnings
├── DeepSeek analysis
│   ├── Classification
│   ├── Confidence
│   ├── Failure analysis
│   └── Source review
└── Test history
```

## 10. DeepSeek Analysis

| Component | Value |
|---|---|
| Runtime | Ollama |
| Default endpoint | `http://127.0.0.1:11434` |
| Environment variable | `OLLAMA_URL` |
| Default model | `deepseek-r1:7b` |
| Model variable | `DEEPSEEK_MODEL` |
| Offline fallback | Deterministic analysis |

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

- DeepSeek confidence `< 0.5`
- DeepSeek inconclusive result
- Unknown root cause
- Repeated failure
- Multi-file modification
- Refactoring
- Architecture change
- Explicit source fix request

```text
DeepSeek
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
- DeepSeek summary
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
│   ├── deepseek/
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
│   └── test/
├── DESIGN.md
├── mkdocs.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

## 15. Final Workflow

```text
Run and Debug: Environment Setup
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
Ollama + DeepSeek
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
