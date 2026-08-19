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

## Repository Structure

```text
.
├── docs/
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
python -m test_envs.tools.environment_setup python --platform config
```

### VS Code 실행 구분

| 영역 | 포함 항목 |
|---|---|
| Run and Debug | Setup, check, extension, report, current Python, current pytest |
| Tasks | Python setup, Ollama setup, environment check, foreground server |
| Launch background process | None |

| Run and Debug Setup | 실행 방식 |
|---|---|
| Setup 1 | OS selection → `test_envs/configs/config.json` |
| Setup 2 | `preLaunchTask` → Python setup Task |
| Setup 3 | `preLaunchTask` → Ollama setup Task |
| Check 1 | `preLaunchTask` → Environment check Task |
| Launch completion | `test_envs.tools.configuration config` → immediate exit |

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
| Config source | `test_envs/configs/config.json` → `os` |
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
| pytest | `test_envs/tests/pytest` | pytest |
| pytest | `test_envs/tests/unittest` | `unittest.TestCase` |
| CT framework unittest | `test_envs/tests/unittest/ct_framework/python` | pytest |

| TEST Task | Scope | VS Code group |
|---|---|---|
| `TEST CASE: ALL` | All registered TEST cases | Default test |
| `TEST CASE: TEST ID` | Marker `test_id` picker | Test |

## 테스트와 리포트

| 작업 | 명령 |
|---|---|
| 전체 TEST | `python -m pytest` |
| CT | `python -m pytest test_envs/tests/pytest -m ct -s` |
| Latest Markdown | `python -m test_envs.tools.test_result` |
| Pending Markdown | `python -m test_envs.tools.test_result --pending` |
| MkDocs publish | `python -m test_envs.tools.test_result --pending --docs` |
| Source review | `python -m test_envs.tools.test_result --pending --docs --source-review` |

## Configuration

```text
test_envs/configs/
├── config.json
├── check.json
└── unittest/                 # Future extension
```

### `test_envs/configs/config.json`

```json
{
  "version": 1,
  "os": "auto",
  "time": {
    "timezone": "Asia/Seoul",
    "utc_offset_hours": 9
  },
  "ollama": {
    "url": "http://127.0.0.1:11434",
    "selected_model": "deepseek-r1:7b",
    "prompt": "result.json 분석",
    "max_timeout_s": 20,
    "max_retry": 3
  }
}
```

| Key | 값 |
|---|---|
| `os` | `auto`, `windows`, `linux`, `macos` |
| `time.timezone` | `Asia/Seoul` |
| `time.utc_offset_hours` | `9` |
| `ollama.url` | Local LLM endpoint |
| `ollama.selected_model` | Ollama model name |
| `ollama.prompt` | Analysis instruction |
| `ollama.max_timeout_s` | Request timeout |
| `ollama.max_retry` | Retry count |

| Model selection priority | Source |
|---:|---|
| 1 | CLI `--model` |
| 2 | `OLLAMA_MODEL` |
| 3 | `test_envs/configs/config.json` |
| Missing | Configuration error |

### `test_envs/configs/check.json`

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
| Environment check | `python -m test_envs.tools.configuration check` |
| Model pull/update | `python -m test_envs.tools.environment_setup ollama --platform config` |
| Foreground server | `python -m test_envs.tools.environment_setup serve --platform config` |
| Report model override | `python -m test_envs.tools.test_result --model "<ollama-model>:<tag>"` |

| Ollama server state | Setup behavior | Completion behavior |
|---|---|---|
| Existing server | Reuse | Preserve |
| Setup task | No server start | Foreground server required |
| VS Code foreground task | Explicit start | Task stop |
| Foreground task + existing server | Duplicate start blocked | Exit `0` |
| Ollama unavailable | Deterministic fallback | Markdown generation |

## 결과 구조

### ID 정의

| Identifier | 적용 대상 | 정의 위치·시점 | 용도 | 형식 |
|---|---|---|---|---|
| TEST ID | pytest only | `test_envs/tests/pytest/test_cases` | Test case 식별 | `CT-<TARGET>-<NNN>` |
| Execution ID | pytest, unittest | Execution result 생성 시점 | Result 구분자 | `YYYYMMDD_HHMMSS_ffffff` |

| Runner | Primary key | TEST ID |
|---|---|---|
| pytest | `TEST ID + Execution ID` | Required |
| unittest | `Execution ID` | Prohibited |

```text
20260819_094832_960333
├── 20260819   # Asia/Seoul date
├── 094832     # Asia/Seoul time
└── 960333     # Microseconds
```

| Time field | 설정 | 처리 |
|---|---|---|
| Timezone | `config.json` → `time.timezone` | SeoulTime 이름 |
| UTC offset | `config.json` → `time.utc_offset_hours` | SeoulTime 보정값 |
| Date·Time | `configured_now()` | Config 값 적용 |
| Microseconds | `%f` | 6자리 |

| Artifact | ID 처리 | 검색 Key |
|---|---|---|
| Result JSON | Execution ID 생성 | Execution ID |
| Test log | Execution ID 재사용 | Execution ID |
| Local LLM log | Execution ID 재사용 | Execution ID |
| Markdown | Execution ID 재사용 | Execution ID |
| Pandoc | Execution ID 재사용 | Execution ID |

```text
Execution ID 검색
├── Result JSON
├── Test log
├── Local LLM log
├── Markdown
└── Pandoc
```

```text
test_envs/reports/
├── results/
│   ├── pytest/test_cases/<test-id>/
│   │   ├── <execution-id>_result.json
│   │   └── <execution-id>_test.log
│   └── unittest/
│       ├── <execution-id>_result.json
│       └── <execution-id>_test.log
├── local_llm/
│   └── <execution-id>_local_llm.log
├── pandoc/<test-id>/
│   └── <execution-id>_result.{html,pdf,docx}
└── markdown/<test-id>/
    └── <execution-id>_result.md
```

| Artifact | 역할 |
|---|---|
| `test_envs/reports/markdown/<test-id>/<execution-id>_result.md` | Canonical human-readable result |
| `<execution-id>_result.json` | Result, measurement, analysis, escalation |
| `<execution-id>_test.log` | Test, stdout, stderr, equipment, interface log |
| `docs/tests/pytest/<test-id>.md` | Latest pytest page |
| `docs/tests/pytest/<test-id>__<execution-id>.md` | pytest execution page |
| `docs/tests/unittest/<execution-id>.md` | unittest execution page |

## Pandoc 변환

| Format | 명령 | 추가 요구사항 |
|---|---|---|
| HTML | `python -m test_envs.tools.pandoc_reporter --latest --format html` | Pandoc PATH |
| DOCX | `python -m test_envs.tools.pandoc_reporter --latest --format docx` | Pandoc PATH |
| PDF | `python -m test_envs.tools.pandoc_reporter --latest --format pdf` | Pandoc PATH + PDF engine |

## 실제 장비 확장

| Layer | Path |
|---|---|
| Test Case | `test_envs/tests/pytest/test_cases/` |
| Equipment Controller | `test_envs/tests/pytest/test_equipments/` |
| DUT Interface | `test_envs/tests/pytest/test_interfaces/` |
| Fixture composition | `test_envs/tests/pytest/fixtures/` |
| Fixture registration / result lifecycle | `test_envs/tests/pytest/conftest.py` |
| CT marker | `@pytest.mark.ct(...)` |
| Result fixture | `ct_result` |

| Fixture composition | Test case | TEST ID |
|---|---|---|
| UART + Saleae | `test_fixture_001_uart_timing.py` | `CT-UART-001` |
| USB + Digilent | `test_fixture_002_usb_loopback.py` | `CT-USB-001` |
| Network | `test_fixture_003_network_loopback.py` | `CT-NETWORK-001` |

| Interface | Mock implementation | unittest | CT |
|---|---|---|---|
| UART | `test_interfaces/uart/mock/mock_uart.py` | `test_mock_uart.py` | `CT-UART-001` |
| USB | `test_interfaces/usb/mock/mock_usb.py` | `test_mock_usb.py` | `CT-USB-001` |
| Network | `test_interfaces/network/mock/mock_network.py` | `test_mock_network.py` | `CT-NETWORK-001` |

| TEST CASE registration | 값 |
|---|---|
| Source | `@pytest.mark.ct` |
| Validation | `pytest_collection_modifyitems` |
| Required fields | `test_id`, `category`, `fixture_id`, `fixture_mode` |
| Fixture ID validation | `test_fixture_<NNN>_*.py` = `FIXTURE-<NNN>` |
| Duplicate TEST ID | Collection error |

| Tool implementation | Tool IDs |
|---|---|
| `test_interfaces/` | `uart`, `usb`, `jtag`, `network` |
| `test_equipments/` | `fpga`, `saleae`, `digilent` |

| Tool implementation | 구분 |
|---|---|
| `<tool>/mock/` | Mock |
| `<tool>/hil/` | Hardware-in-the-loop |

| Mode | Field | Source |
|---|---|---|
| TEST | `fixture_mode` | `@pytest.mark.ct` |
| Interface | `interface_mode` | `fixture_mode` |
| Equipment | `equipment_mode` | `fixture_mode` / `none` |

| Fixture | Combination |
|---|---|
| `fixture_001_uart_saleae.py` | UART + Saleae |
| `fixture_002_usb_digilent.py` | USB + Digilent |
| `fixture_003_network.py` | Network |
| `fixture_004_jtag_fpga.py` | JTAG mock + FPGA mock |
| `fixture_005_full_hil.py` | Full HIL gate |

| Mode source | Priority |
|---|---:|
| CLI `--fixture-mode=mock|hil` | 1 |
| Marker `fixture_mode` | 2 |

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
