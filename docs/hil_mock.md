# pytest HIL / Mock

## 적용 범위

| Runner | Mock / HIL 적용 |
|---|---|
| pytest | O |
| unittest | X |

## Mode 정의

| Mode | Interface | Equipment | DUT |
|---|---|---|---|
| `mock` | Mock implementation | Mock controller | Simulation / loopback |
| `hil` | Hardware implementation | Hardware controller | Physical DUT |
| `none` | 미사용 | 미사용 | 해당 없음 |

## Mode 값

| Result field | Source |
|---|---|
| `test_mode` | Effective fixture mode |
| `interface_mode` | Effective fixture mode |
| `equipment_mode` | Effective fixture mode / `none` |

## 선택 우선순위

| Priority | Source | Value |
|---:|---|---|
| 1 | CLI | `--fixture-mode=mock`, `--fixture-mode=hil` |
| 2 | `@pytest.mark.ct` | `fixture_mode="mock"`, `fixture_mode="hil"` |

```text
CLI mock / hil
      │
      ├── 지정됨 ──► CLI mode
      │
      └── marker ──► @pytest.mark.ct fixture_mode
                         │
                         ▼
                  Effective fixture mode
```

## Marker

```python
@pytest.mark.ct(
    test_id="CT-UART-001",
    category="timing",
    fixture_id="FIXTURE-001",
    fixture_mode="mock",
    interface="UART",
    equipment="Saleae",
)
```

| Field | Rule |
|---|---|
| `test_id` | pytest TEST ID |
| `fixture_id` | Test filename mapping |
| `fixture_mode` | Marker 기본 mode |
| CLI override | Marker보다 우선 |

## Directory

```text
test_envs/tests/pytest/
├── test_interfaces/
│   ├── usb/{mock,hil}/
│   ├── uart/{mock,hil}/
│   ├── jtag/{mock,hil}/
│   └── network/{mock,hil}/
└── test_equipments/
    ├── fpga/{mock,hil}/
    ├── saleae/{mock,hil}/
    └── digilent/{mock,hil}/
```

## Fixture 동작

```text
Test case
   │
   ▼
Composite fixture
   ├── Effective fixture mode
   ├── Test Interface
   ├── Test Equipment
   ├── connect
   ├── yield
   └── disconnect
```

| Fixture | Composition | Mock | HIL |
|---|---|---|---|
| `FIXTURE-001` | UART + Saleae | 구현 | 미구현·명시적 FAIL |
| `FIXTURE-002` | USB + Digilent | 구현 | 미구현·명시적 FAIL |
| `FIXTURE-003` | Network | 구현 | 미구현·명시적 FAIL |
| `FIXTURE-004` | JTAG + FPGA | Mock fixture | 확장 대상 |
| `FIXTURE-005` | Full HIL gate | 해당 없음 | `CICT_HIL=1` gate |

## 실행 명령

### Marker mode

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=marker
```

### Mock

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=mock
```

### HIL

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=hil
```

### TEST ID

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --test-id CT-UART-001 --fixture-mode=mock
```

## VS Code

| Item | Value |
|---|---|
| Task | `TEST CASE: ALL` |
| Task | `TEST CASE: TEST ID` |
| Input | `fixtureMode` |
| Options | `marker`, `mock`, `hil` |

## Result JSON

```text
fixture_configs
├── test_mode
├── interface_mode
├── equipment_mode
├── interface
└── equipment
```

## HIL Gate

| Check | Rule |
|---|---|
| Hardware implementation | Required |
| Interface connection | Required |
| Equipment connection | Required |
| DUT availability | Required |
| Cleanup | `finally` disconnect |
| Missing implementation | Explicit FAIL / SKIP |
| Silent Mock fallback | Prohibited |
