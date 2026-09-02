# Pytest 


## Scope

| Area | Coverage |
|---|---|
| Communication | USB, UART, JTAG, Network |
| Timing | Baudrate, jitter, latency, frequency |
| Functional | DUT feature validation |
| Performance | Throughput, response time, load |
| Stability | Repetition, duration, recovery |
| Regression | Previous failure and baseline comparison |

## Communication CT

| Test ID | Interface | Scope |
|---|---|---|
| `CT-USB-001` | USB | Bulk loopback / packetization / integrity |
| `CT-NETWORK-001` | Network | Packet loopback / latency / integrity |

## TEST CASE Marker

| Item | Value |
|---|---|
| Source | `@pytest.mark.ct` |
| Required fields | `test_id`, `category`, `fixture_id`, `fixture_mode` |
| Optional prompt | `test_prompt` |
| Prompt fallback | `ollama.default_prompt` |
| Mode selection | `fixture_mode` |
| Tool selection | `FIXTURE_META.interfaces`, `FIXTURE_META.equipments` |
| Supported modes | `FIXTURE_META.modes` |
| Derived modes | `interface_mode`, `equipment_mode` |
| Validation | Marker + filename + fixture argument + `FIXTURE_META` |
| Missing / duplicate / invalid mode | Collection error |

## Fixture metadata

| Field | Type |
|---|---|
| `fixture_id` | `str` |
| `interfaces` | `list[str]` |
| `equipments` | `list[str]` |
| `modes.mock.enabled` | `bool` |
| `modes.hil.enabled` | `bool` |

| Ownership | Fields |
|---|---|
| Test case marker | `test_id`, `category`, `fixture_id`, `fixture_mode`, `test_prompt` |
| Fixture | `interfaces`, `equipments`, `modes` |

| Directory | Tools |
|---|---|
| `test_envs/tests/pytest/test_equipments/` | FPGA, Saleae, Digilent |
| `test_envs/tests/pytest/test_interfaces/` | USB, UART, JTAG, Network |

## Structure

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
    ├── ct_framework/
    │   └── python/
    ├── python/
    ├── c_cpp/
    ├── firmware/
    └── common/
```

## Fixture-to-Test Mapping

| Order | Fixture composition | Test case | TEST ID |
|---:|---|---|---|
| 1 | UART + Saleae | `test_fixture_001_uart_timing.py` | `CT-UART-001` |
| 2 | USB + Digilent | `test_fixture_002_usb_loopback.py` | `CT-USB-001` |
| 3 | Network | `test_fixture_003_network_loopback.py` | `CT-NETWORK-001` |

## Mock / HIL

| Scope | Document |
|---|---|
| pytest only | [Open](hil_mock.md) |

## Execution Model

```mermaid
flowchart TD
    A[pytest Test Case] --> B[Fixture]
    B --> C[Test Interface]
    B --> D[Test Equipment]
    C --> E[DUT]
    D --> E
    A --> F[Result Recorder]
    F --> G[Result + Log + Measurement]
```

## Commands

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest -m ct -s
```

## Report Files

| Type | Path |
|---|---|
| Result | `test_envs/reports/results/pytest/test_cases/<test-id>/<timestamp>_result.json` |
| Log | `test_envs/reports/results/pytest/test_cases/<test-id>/<timestamp>_test.log` |
| Markdown | `test_envs/reports/markdown/<test-id>/<timestamp>_result.md` |
| Pandoc | `test_envs/reports/pandoc/<test-id>/<timestamp>_result.<format>` |

## VS Code

- Testing path: `test_envs/tests/pytest`
- Debug: `Debug: Current pytest File`
- Task: `TEST CASE: ALL`
- Task: `TEST CASE: TEST ID` / ID list
