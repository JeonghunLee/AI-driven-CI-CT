# pytest / Continuous Testing

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

## TEST CASE Registry

| Item | Value |
|---|---|
| File | `test_envs/tests/pytest/test_cases/catalog.json` |
| Key | `test_id` |
| Mode selection | `test_mode` |
| Derived modes | `interface_mode`, `equipment_mode` |
| Validation | pytest collection hook |
| Missing / mismatch | Collection error |

| Registry | Tools |
|---|---|
| `test_equipments/catalog.json` | FPGA, Saleae, Digilent |
| `test_interfaces/catalog.json` | USB, UART, JTAG, Network |

## Structure

```text
test_envs/tests/
├── pytest/
│   ├── test_cases/
│   │   ├── communication/
│   │   ├── timing/
│   │   ├── functional/
│   │   ├── performance/
│   │   ├── stability/
│   │   └── regression/
│   ├── fixtures/
│   │   ├── fixture_001_uart.py
│   │   ├── fixture_002_uart_saleae.py
│   │   ├── fixture_003_usb_digilent.py
│   │   ├── fixture_004_jtag_fpga.py
│   │   ├── fixture_005_full_hil.py
│   │   └── fixture_006_network.py
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

## VS Code

- Testing path: `test_envs/tests/pytest`
- Debug: `Debug: Current pytest File`
- Task: `TEST CASE: ALL`
- Task: `TEST CASE: TEST ID` / ID list
