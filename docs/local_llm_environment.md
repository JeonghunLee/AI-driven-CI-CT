# Local LLM Environment

## Components

| Item | Value |
|---|---|
| Runtime | Ollama |
| Endpoint | `http://127.0.0.1:11434` |
| Config | `test_envs/configs/config.json → ollama` |
| Check | `test_envs/configs/check.json → ollama` |
| Default model | `deepseek-r1:7b` |
| Model ownership | Config JSON |

## Config

```json
{
  "ollama": {
    "url": "http://127.0.0.1:11434",
    "selected_model": "deepseek-r1:7b",
    "default_prompt": "analyze the test result and provide a detailed report with recommendations for improvement.",
    "max_timeout_s": 20,
    "max_retry": 3
  }
}
```

| Field | Rule |
|---|---|
| `url` | Ollama API endpoint |
| `selected_model` | Pull and analysis model |
| `default_prompt` | Empty `test_prompt` fallback |
| `max_timeout_s` | Request timeout |
| `max_retry` | Retry count |

## Setup

```text
Ollama installation check
      ↓
OS installer
      ↓
Foreground server
      ↓
Model inventory
      ↓
ollama pull <selected_model>
```

| OS | Installer |
|---|---|
| Windows | `winget install Ollama.Ollama` |
| macOS | `brew install ollama` |
| Linux | Ollama installer |

## VS Code

| Item | Value |
|---|---|
| Launch | `SETUP 3: Install Ollama and Local LLM` |
| Task | `SETUP 3: Install Ollama and Local LLM` |
| Check | `CHECK 1: Refresh Environment Check File` |
| Server | `CHECK 3: Run Ollama Server (Foreground)` |
| Background server | Prohibited |

## Commands

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.environment_setup ollama
.\.venv\Scripts\python.exe -m test_envs.tools.environment_setup serve
.\.venv\Scripts\python.exe -m test_envs.tools.configuration check
```

## Check file

```text
ollama
├── installed
├── executable
├── version
├── available
├── endpoint
├── selected_model
├── selected_model_installed
└── supported_models[]
```

## Test usage

| Runner | Local LLM |
|---|---:|
| pytest | O |
| unittest | X |

| pytest prompt | Priority |
|---|---:|
| Non-empty marker `test_prompt` | 1 |
| `ollama.default_prompt` | 2 |

## Logs

| Runner | Output |
|---|---|
| pytest | `test_envs/reports/local_llm/<execution-id>_local_llm.log` |
| unittest | None |
