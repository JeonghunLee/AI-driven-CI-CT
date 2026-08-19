# pytest HIL / Mock

## Scope

| Runner | Mock / HIL |
|---|---|
| pytest | O |
| unittest | X |

## Mode

| Mode | Interface | Equipment | DUT |
|---|---|---|---|
| `mock` | Mock implementation | Mock controller | Simulation / loopback |
| `hil` | Hardware implementation | Hardware controller | Physical DUT |
| `none` | N/A | N/A | N/A |

## Priority

| Priority | Source | Value |
|---:|---|---|
| 1 | CLI | `--fixture-mode=mock`, `--fixture-mode=hil` |
| 2 | Marker | `fixture_mode="mock"`, `fixture_mode="hil"` |

## Test case marker

```python
@pytest.mark.ct(
    test_id="CT-UART-001",
    category="timing",
    fixture_id="FIXTURE-001",
    fixture_mode="mock",
    test_prompt="",
)
```

| Field | Owner |
|---|---|
| `test_id` | Test case |
| `category` | Test case |
| `fixture_id` | Test case → Fixture mapping |
| `fixture_mode` | Test case default mode |
| `test_prompt` | Test case LLM prompt override |
| `interfaces` | Fixture |
| `equipments` | Fixture |
| `modes` | Fixture |

## Fixture metadata

```python
FIXTURE_META = {
    "fixture_id": "FIXTURE-001",
    "interfaces": [
        "UART",
    ],
    "equipments": [
        "Saleae",
    ],
    "modes": {
        "mock": {
            "enabled": True,
        },
        "hil": {
            "enabled": True,
        },
    },
}
```

| Validation | Rule |
|---|---|
| `fixture_id` | Unique, non-empty |
| `interfaces` | `list[str]` |
| `equipments` | `list[str]`; empty list allowed |
| `modes.mock.enabled` | `bool` |
| `modes.hil.enabled` | `bool` |
| Marker mode | Enabled in `FIXTURE_META` |
| CLI override mode | Enabled in `FIXTURE_META` |
| Test filename | `test_fixture_<NNN>_*.py` |
| Fixture ID | `FIXTURE-<NNN>` |
| Fixture argument | `fixture_<NNN>` |

## Mapping

| Fixture | Interfaces | Equipments | Mock | HIL |
|---|---|---|---:|---:|
| `FIXTURE-001` | UART | Saleae | O | O |
| `FIXTURE-002` | USB | Digilent | O | O |
| `FIXTURE-003` | Network | - | O | O |
| `FIXTURE-004` | JTAG | FPGA | O | X |
| `FIXTURE-005` | - | - | X | O |

## Execution

```powershell
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=marker
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=mock
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --fixture-mode=hil
.\.venv\Scripts\python.exe -m pytest test_envs/tests/pytest/test_cases --test-id CT-UART-001 --fixture-mode=mock
```

## Result JSON

```text
fixture_configs
├── fixture_id
├── test_mode
├── interface_mode
├── equipment_mode
├── interfaces[]
├── equipments[]
└── modes
    ├── mock.enabled
    └── hil.enabled
```

## HIL gate

| Check | Rule |
|---|---|
| `modes.hil.enabled` | Required |
| Hardware implementation | Required |
| Interface connection | Required |
| Equipment connection | Required when configured |
| Cleanup | `finally` disconnect |
| Missing implementation | Explicit FAIL / SKIP |
| Silent Mock fallback | Prohibited |
