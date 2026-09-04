# AI-driven Continuous Testing

## System Overview

<br/>

| Area | Role |
|---|---|
| VS Code | Common entry point for Testing, Tasks, debugging, and environment setup |
| GitHub Actions | CI entry point for hosted Mock/unit tests and optional self-hosted hardware tests |
| pytest CT | Runs TEST ID scenarios using a final `mock` or `hil` fixture mode |
| unittest | Runs function-level framework and extension tests without TEST ID or fixture mode |
| Result pipeline | Normalizes execution data and generates Markdown reports |
| Local LLM | Analyzes pytest CT results only; it is not used for unittest |
| MkDocs | Publishes pytest and unittest Markdown and execution history |

<br/>

Go to [VSCode Testing](https://jeonghunlee.github.io/vscode_doc/#vscode-testing)  

!!! success "AI Agent workflow based on MCP"   
    Connect Claude, Codex, Ollama, and GitHub operations through MCP  
    Support Local MCP execution, GitHub Issue based TEST automation, and documentation-first project flow    
    https://jeonghunlee.github.io/local-ai-agent-mcp/index.html


<br/>

## Documents

<br/>

| Scope | Document | Components |
|---|---|---|
| Python Environment | [python_environment.md](python_environment.md) | OS, Python, venv, dependencies |
| Local LLM Environment | [local_llm_environment.md](local_llm_environment.md) | Ollama, model, prompt, check |
| VS Code Environment | [vscode_environment.md](vscode_environment.md) | Settings, Launch, Tasks, Testing |
| Pytest Operation | [pytest_operation.md](pytest_operation.md) | TEST ID, Fixture, Mock/HIL, Local LLM |
| Unittest Operation | [unittest_operation.md](unittest_operation.md) | Function, Execution ID, Result, Markdown |
| Pytest / HIL / Mock | [pytest_framework.md](pytest_framework.md) | Test cases, fixture mapping, mode selection, HIL gate |
| Unittest | [unittest_framework.md](unittest_framework.md) | Function result contract |
| Pytest Results | [tests/pytest/index.md](tests/pytest/index.md) | TEST ID, Execution history |
| Unittest Results | [tests/unittest/index.md](tests/unittest/index.md) | Function count, Execution history |

<br/>

## TEST Flow

<br/>

### VS Code-based flow

<br/>


Go To [VS Code Testing Setup](https://jeonghunlee.github.io/vscode_doc/#settingjson)   
Go To [VS Code Testing](https://jeonghunlee.github.io/vscode_doc/#vscode-testing)    

<br/>

```mermaid
flowchart TD
    VSCODE[VS Code]
    EXTENSION[VS Extension Testing]
    TASK[VS Code Task]
    ENV[TEST System Environment]
    PYTEST[Pytest Operation]
    UNITTEST[Unittest Operation]
    PYTEST_RESULT[Pytest Result]
    UNITTEST_RESULT[Unittest Result]
    LLM[Local LLM]
    REPORTER["**src:test_envs/tools/mkdocs_reporter**<br/>MarkdownReporter"]
    MARKDOWN["Pytest / Unittest Markdown"]
    MKDOCS["MkDocs (TEST Results)"]
    PANDOC_REPORTER["**src:test_envs/tools/pandoc_reporter**<br/>convert"]
    PANDOC[Pandoc Report - HTML / DOCX]

    VSCODE --> EXTENSION
    VSCODE --> TASK
    TASK --> ENV
    ENV -. Runtime and configuration .-> EXTENSION

    EXTENSION --> PYTEST
    EXTENSION --> UNITTEST
    TASK --> PYTEST

    PYTEST --> PYTEST_RESULT --> LLM --> REPORTER
    UNITTEST --> UNITTEST_RESULT --> REPORTER

    TASK --> REPORTER
    REPORTER --> MARKDOWN
    MARKDOWN --> MKDOCS
    MARKDOWN --> PANDOC_REPORTER --> PANDOC
    TASK --> MKDOCS
    TASK --> PANDOC_REPORTER

    classDef testResults fill:#fff3bf,stroke:#f08c00,stroke-width:4px,color:#5f3d00,font-weight:bold
    class MKDOCS testResults
```

<br/>

| VS Code entry | Execution scope |
|---|---|
| VS Extension Testing | Discovers and runs both pytest CT and unittest through the pytest adapter |
| VS Code Task | Prepares the environment, runs pytest CT, generates MkDocs reports, and converts the latest Markdown to Pandoc HTML/DOCX |
| Common Markdown reporter | `test_envs/tools/mkdocs_reporter` renders both pytest and unittest results through `MarkdownReporter` |
| Pandoc reporter | `test_envs/tools/pandoc_reporter` converts the latest common Markdown report to HTML or DOCX |


!!! success "Automatically Generate Report"
    Analyze Result.log and result.json using an LLM, 
    then automatically update the analysis report in the **MkDocs documentation.**    
    
    * **Left Menu TEST Results**    
        * Go To [TEST Results Pytest](./tests/pytest/index.md)   
        * Go To [TEST Results Unittest](./tests/unittest/index.md)       



<br/>

### GitHub Actions-based flow

<br/>

```mermaid
flowchart TD
    GITHUB[GitHub Actions]
    CONTINUOUS[continuous-test.yml]
    SPECIAL[special-environment-test.yml]
    ENV[TEST System Environment]
    PYTEST[Pytest Operation]
    UNITTEST[Unittest Operation]
    PYTEST_RESULT[Pytest Result]
    UNITTEST_RESULT[Unittest Result]
    LLM[Local LLM]
    REPORTER["test_envs/tools/mkdocs_reporter<br/>MarkdownReporter"]
    MARKDOWN["Pytest / Unittest Markdown"]
    MKDOCS["MkDocs (TEST Results)"]
    ISSUE[GitHub Issue Comment]
    ARTIFACT[GitHub Artifact]

    GITHUB --> CONTINUOUS
    GITHUB --> SPECIAL
    CONTINUOUS --> ENV
    SPECIAL --> ENV

    CONTINUOUS -->|Mock CT| PYTEST
    CONTINUOUS -->|Unit Test| UNITTEST
    SPECIAL -->|Special pytest path| PYTEST

    PYTEST --> PYTEST_RESULT --> LLM --> REPORTER
    UNITTEST --> UNITTEST_RESULT --> REPORTER

    REPORTER --> MARKDOWN
    MARKDOWN --> MKDOCS
    CONTINUOUS --> ISSUE
    MARKDOWN --> ARTIFACT

    classDef testResults fill:#fff3bf,stroke:#f08c00,stroke-width:4px,color:#5f3d00,font-weight:bold
    class MKDOCS testResults
```

<br/>

| GitHub Actions entry | Execution scope |
|---|---|
| `continuous-test.yml` | Runs unittest or Mock CT on a GitHub-hosted Ubuntu runner, generates reports, comments on issue requests, and uploads evidence |
| `special-environment-test.yml` | Runs a selected pytest path on a self-hosted hardware runner, generates a report, and uploads evidence |
| Common Markdown reporter | `test_envs/tools/mkdocs_reporter` renders both result types before MkDocs publication and artifact upload |

<br/>

## GitHub Actions Flow

<br/>

### `continuous-test.yml`

| Item | Current behavior |
|---|---|
| Workflow name | `Continuous Test` |
| Trigger | Issue labeled `run-test` or manual `workflow_dispatch` |
| Job condition | Manual run, or the added issue label is exactly `run-test` |
| Runner | `ubuntu-latest` |
| Timeout | 30 minutes |
| Permissions | Repository contents read; issues write |
| Python | `actions/setup-python@v5`, Python 3.12, pip cache |
| Environment | Creates `.venv` and installs `requirements.txt` |
| Request routing | `test_envs.tools.issue_parser` selects Unit Test or CT |
| Unit Test | pytest over `test_envs/tests/unittest`, then JUnit normalization |
| CT | Selected TEST ID under `test_envs/tests/pytest/test_cases`; current marker defaults produce Mock CT |
| Report | `test_envs.tools.pipeline --docs` runs even after test failure |
| Issue output | `test_envs.tools.github_reporter` comments when an issue number exists |
| Artifact | Uploads `test_envs/reports/` and published pytest/unittest documents |

The manual `runner` input currently accepts `Default`, `Windows`, or `Linux`, but the job's `runs-on` remains fixed to `ubuntu-latest`; that input does not select a runner in the current workflow.

<br/>

### `special-environment-test.yml`

<br/>

| Item | Current behavior |
|---|---|
| Workflow name | `Optional Special Environment Test` |
| Trigger | Manual `workflow_dispatch` only |
| Input | `test_path`, default `test_envs/tests/pytest` |
| Runner | `[self-hosted, hw-test]` |
| Timeout | 60 minutes |
| Shell | PowerShell (`pwsh`) |
| Environment | Reuses `.venv` when present or creates it, then installs `requirements.txt` |
| Test | Executes pytest for the selected special hardware/environment path |
| Report | `test_envs.tools.pipeline --docs` runs even after test failure |
| Artifact | Uploads `test_envs/reports/` as `special-test-<run-id>` |

<br/>

### Workflow roles

<br/>

| Workflow | Primary role | Local LLM rule |
|---|---|---|
| `continuous-test.yml` | Repeatable hosted Unit Test and Mock CT automation | Used only when the selected result is pytest CT; unittest bypasses it |
| `special-environment-test.yml` | Optional hardware, vendor-tool, internal-network, or machine-specific testing | Used for pytest CT results; unavailable Ollama falls back to deterministic analysis |

<br/>

## Test System Paths

<br/>

```
.
├── .github/
│   └── workflows/
│       ├── continuous-test.yml
│       ├── special-environment-test.yml
│       └── github_pages.yaml
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── docs/
├── site/
└── test_envs/
    ├── configs/
    │   ├── config.json
    │   ├── check.json
    │   ├── pytest/
    │   └── unittest/
    ├── tests/
    ├── reports/
    └── tools/
```
<br/>

| Scope | Path |
|---|---|
| Project config | `test_envs/configs/config.json` |
| Environment check | `test_envs/configs/check.json` |
| pytest | `test_envs/tests/pytest` |
| unittest | `test_envs/tests/unittest` |
| Results | `test_envs/reports/results` |
| Local LLM logs | `test_envs/reports/local_llm` |
| Markdown | `test_envs/reports/markdown` |
| Pandoc | `test_envs/reports/pandoc` |

<br/>

## Identifier

<br/>

| Identifier | pytest | unittest | Format |
|---|---:|---:|---|
| TEST ID | O | X | `CT-<TARGET>-<NNN>` |
| Execution ID | O | O | `YYYYMMDD_HHMMSS_ffffff` |

<br/>

## Local LLM

<br/>

The Local LLM is part of the pytest report branch only. A unittest result is converted directly to Markdown without an Ollama request, Local LLM log, analysis payload, or escalation decision.

<br/>

| Runner | Local LLM | Processing rule |
|---|---:|---|
| pytest CT | O | Analyze result, logs, warnings, and optional source diff before Markdown generation |
| unittest | X | Generate execution summary and function results directly from normalized data |

<br/>

### Local LLM roles

<br/>

| Role | Input | Output / decision |
|---|---|---|
| Evidence collection | Pytest result JSON, errors, warnings, important log lines | Bounded evidence payload; no invented evidence |
| Prompt selection | Non-empty CT marker `test_prompt`; otherwise configured `ollama.default_prompt` | Effective analysis instruction |
| Result summary | Status, duration, metrics, statistics, and logs | Human-readable `summary` |
| Failure classification | Result status and captured failure evidence | `classification` and `failure_analysis` |
| Confidence estimation | Available test and log evidence | `confidence` from `0.0` to `1.0` |
| Warning analysis | Captured warning lines | Structured warnings with `Critical`, `Important`, or `Low` severity |
| Source review | Optional local Git diff from `--source-review` | `source_review`; otherwise `Not requested` |
| Recommendation | Analysis findings | Actionable `recommendations` |
| Escalation judgment | LLM escalation flag, confidence, failure classification, and repeated failures | `needs_escalation` plus Codex escalation reasons |
| Offline fallback | Ollama request failure or invalid response | Deterministic summary, classification, warnings, and recommendation |

<br/>

### Pytest analysis flow

<br/>

```text
Pytest Result JSON + Test Log
             +
Optional Source Diff
             ↓
Prompt selection
├── @pytest.mark.ct(test_prompt="...")
└── ollama.default_prompt
             ↓
Local LLM / Deterministic Fallback
             ↓
Test analysis + Escalation decision
             ↓
Pytest Markdown + MkDocs
```

<br/>

| Item | Path / rule |
|---|---|
| Runtime | Ollama |
| Configuration | `test_envs/configs/config.json → ollama` |
| Analysis payload | Pytest result JSON → `test_analysis` |
| Diagnostic log | `test_envs/reports/local_llm/<execution-id>_local_llm.log` |
| Unittest Local LLM log | Not generated |
| Detailed setup | [local_llm_environment.md](local_llm_environment.md) |

<br/>
