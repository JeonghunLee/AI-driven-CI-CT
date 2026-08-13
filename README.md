# AI-driven Continuous Testing

| 항목 | 구성 |
|---|---|
| Development | VS Code |
| Python | Project-local `.venv` |
| Unit Test | `unittest` |
| Continuous Test | `pytest` |
| Local LLM | Ollama |
| Result source | Markdown |
| Web documentation | MkDocs |
| Document conversion | Pandoc |
| Design | [DESIGN.md](DESIGN.md) |

## 구성

- VS Code Testing / Run and Debug
- Python Unit Test
- C/C++ / Firmware extension structure
- Integration / Functional / Hardware CT
- Test Equipment / Test Interface separation
- Mock UART / Mock Saleae UART Timing CT
- Ollama Local LLM
- Markdown execution history
- GitHub-hosted runner
- Optional self-hosted hardware runner
- Codex escalation

## 환경 준비

| Platform | Bootstrap Python |
|---|---|
| Windows | `python` |
| Linux | `python3` |
| macOS | `python3` |

```text
python -m tools.environment_setup python --platform config
```

### VS Code 실행 구분

| 영역 | 포함 항목 |
|---|---|
| Run and Debug | Setup, check, extension, report, current Python, current pytest |
| Tasks | Python setup, Ollama setup, environment check, foreground server |
| Launch background process | None |

| Run and Debug Setup | 실행 방식 |
|---|---|
| Setup 1 | OS selection → `config/config.json` |
| Setup 2 | `preLaunchTask` → Python setup Task |
| Setup 3 | `preLaunchTask` → Ollama setup Task |
| Check 1 | `preLaunchTask` → Environment check Task |
| Launch completion | `tools.configuration config` → immediate exit |

| Setup 1 runtime | 값 |
|---|---|
| Launch Python | `python` |
| Task Python | `python` |
| `.venv` detected | System Python re-exec |
| System Python detected | Direct execution |
| Resolution source | `sys._base_executable` |

| Setup 1 OS input | 값 |
|---|---|
| Default | `auto` |
| Options | `auto`, `windows`, `linux`, `macos` |
| Config source | `config/config.json` → `os` |
| Host mismatch | Setup stop |
| Setup 1·2 Python | `python` |
| Setup 3+ Python | `${config:python.defaultInterpreterPath}` |
| OS-specific path | `.vscode/settings.json` only |
| Testing interpreter sync | Setup 1 → `.vscode/settings.json` |
| Test discovery | Save-triggered automatic discovery |
| VS Code pytest cache | Disabled |

### VS Code Testing

| Adapter | Discovery path | Implementation |
|---|---|---|
| pytest | `tests/pytest` | pytest |
| pytest | `tests/unittest` | `unittest.TestCase` |
| Native unittest task | `tests/unittest` | unittest discovery |

| TEST Task | Scope | VS Code group |
|---|---|---|
| `TEST CASE: ALL` | All registered TEST cases | Default test |
| `TEST CASE: TEST ID` | Prompted `test_id` | Test |

## 테스트와 리포트

| 작업 | 명령 |
|---|---|
| 전체 TEST | `python -m pytest` |
| CT | `python -m pytest tests/pytest -m ct -s` |
| Latest Markdown | `python -m test_result` |
| MkDocs publish | `python -m test_result --docs` |
| Source review | `python -m test_result --docs --source-review` |

## Configuration

```text
config/
├── config.json   # User selection
└── check.json    # Generated environment state
```

### `config/config.json`

```json
{
  "version": 1,
  "os": "auto",
  "ollama": {
    "url": "http://127.0.0.1:11434",
    "selected_model": "deepseek-r1:7b"
  }
}
```

| Key | 값 |
|---|---|
| `os` | `auto`, `windows`, `linux`, `macos` |
| `ollama.url` | Local LLM endpoint |
| `ollama.selected_model` | Ollama model name |

| Model selection priority | Source |
|---:|---|
| 1 | CLI `--model` |
| 2 | `OLLAMA_MODEL` |
| 3 | `config/config.json` |
| Missing | Configuration error |

### `config/check.json`

| Check | Field |
|---|---|
| OS configuration | `os.configured` |
| OS detection | `os.detected`, `os.name` |
| Python installation | `python.installed` |
| Python runtime | `python.executable`, `python.version` |
| Ollama installation | `ollama.installed` |
| Ollama runtime | `ollama.executable`, `ollama.version`, `ollama.available` |
| Selected model | `ollama.selected_model`, `ollama.selected_model_installed` |
| Installed models | `ollama.supported_models` |

| 작업 | 명령 |
|---|---|
| Environment check | `python -m tools.configuration check` |
| Model pull/update | `python -m tools.environment_setup ollama --platform config` |
| Foreground server | `python -m tools.environment_setup serve --platform config` |
| Report model override | `python -m test_result --model "<ollama-model>:<tag>"` |

| Ollama server state | Setup behavior | Completion behavior |
|---|---|---|
| Existing server | Reuse | Preserve |
| Setup task | No server start | Foreground server required |
| VS Code foreground task | Explicit start | Task stop |
| Foreground task + existing server | Duplicate start blocked | Exit `0` |
| Ollama unavailable | Deterministic fallback | Markdown generation |

## 결과 구조

```text
reports/
├── logs/<test-id>/<execution-id>/
│   ├── result.json
│   ├── analysis.json
│   ├── codex-escalation.json
│   ├── test.log
│   ├── stdout.log
│   ├── stderr.log
│   ├── equipment.log
│   └── interface.log
├── measurements/<test-id>/<execution-id>/
│   ├── measurement.json
│   └── measurement.csv
└── markdown/<test-id>/
    ├── latest.md
    └── <execution-id>/result.md
```

| Artifact | 역할 |
|---|---|
| `reports/markdown/.../result.md` | Canonical human-readable result |
| `result.json` | Machine-readable intermediate data |
| `test_result/markdown/latest.md` | Latest report copy |
| `docs/test/.../<test-id>.md` | Latest MkDocs TEST page |
| `docs/test/.../<test-id>/<execution-id>.md` | Append-only execution page |

## Pandoc 변환

| Format | 명령 | 추가 요구사항 |
|---|---|---|
| HTML | `python -m tools.pandoc_reporter --latest --format html` | Pandoc PATH |
| DOCX | `python -m tools.pandoc_reporter --latest --format docx` | Pandoc PATH |
| PDF | `python -m tools.pandoc_reporter --latest --format pdf` | Pandoc PATH + PDF engine |

## 실제 장비 확장

| Layer | Path |
|---|---|
| Test Case | `tests/pytest/test_cases/` |
| Equipment Controller | `tests/pytest/test_equipments/` |
| DUT Interface | `tests/pytest/test_interfaces/` |
| Lifecycle fixture | `tests/pytest/conftest.py` |
| CT marker | `@pytest.mark.ct(...)` |
| Result fixture | `ct_result` |

| Interface | Mock implementation | unittest | CT |
|---|---|---|---|
| UART | `test_interfaces/uart/mock_uart.py` | `test_mock_uart.py` | `CT-UART-001` |
| USB | `test_interfaces/usb/mock_usb.py` | `test_mock_usb.py` | `CT-USB-001` |
| Network | `test_interfaces/network/mock_network.py` | `test_mock_network.py` | `CT-NETWORK-001` |

| TEST CASE registration | 값 |
|---|---|
| Catalog | `tests/pytest/test_cases/catalog.json` |
| Validation | `pytest_collection_modifyitems` |
| Unregistered CT | Collection error |
| Module mismatch | Collection error |

| Tool registry | Tool IDs |
|---|---|
| `test_interfaces/catalog.json` | `uart`, `usb`, `jtag`, `network` |
| `test_equipments/catalog.json` | `fpga`, `saleae`, `digilent` |

| Tool implementation | 구분 |
|---|---|
| `<tool>/mock/` | Mock |
| `<tool>/hil/` | Hardware-in-the-loop |

| Mode | Field | Source |
|---|---|---|
| TEST | `test_mode` | `test_cases/catalog.json` |
| Interface | `interface_mode` | `test_mode` |
| Equipment | `equipment_mode` | `test_mode` / `none` |

| Fixture | Combination |
|---|---|
| `fixture_001_uart.py` | UART mock |
| `fixture_002_uart_saleae.py` | UART mock + Saleae mock |
| `fixture_003_usb_digilent.py` | USB mock + Digilent mock |
| `fixture_004_jtag_fpga.py` | JTAG mock + FPGA mock |
| `fixture_005_full_hil.py` | Full HIL gate |
| `fixture_006_network.py` | Network mock |

| TEST Program | Interface Tool | Equipment Tool |
|---|---|---|
| `CT-UART-001` | `uart` | `saleae` |
| `CT-USB-001` | `usb` | `digilent` |
| `CT-NETWORK-001` | `network` | None |

## GitHub 자동화

| Workload | Runner |
|---|---|
| Unit Test | GitHub-hosted |
| Mock CT | GitHub-hosted |
| USB / JTAG / vendor tool / internal network | `[self-hosted, hw-test]` |
| Special workflow | `Optional Special Environment Test` |
