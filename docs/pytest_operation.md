# Pytest Operation

## Identifier

| Identifier | Rule | Format |
|---|---|---|
| TEST ID | Required | `CT-<TARGET>-<NNN>` |
| Fixture ID | Required | `FIXTURE-<NNN>` |
| Execution ID | Required | `YYYYMMDD_HHMMSS_ffffff` |

## Runtime

```text
Test case marker
├── test_id
├── category
├── fixture_id
├── fixture_mode
└── test_prompt
       ↓
Fixture FIXTURE_META
├── interfaces[]
├── equipments[]
└── modes
       ↓
pytest execution
       ↓
Result JSON + Test log
       ↓
Local LLM
       ↓
Markdown + MkDocs
```

## Structure

```text
test_envs/tests/pytest/
├── test_cases/
├── fixtures/
├── test_interfaces/{usb,uart,jtag,network}/{mock,hil}/
├── test_equipments/{fpga,saleae,digilent}/{mock,hil}/
└── conftest.py
```

## Mode

| Priority | Source |
|---:|---|
| 1 | CLI `--fixture-mode=mock|hil` |
| 2 | Marker `fixture_mode` |

| Validation | Source |
|---|---|
| Mode enabled | `FIXTURE_META.modes.<mode>.enabled` |
| Interface | `FIXTURE_META.interfaces` |
| Equipment | `FIXTURE_META.equipments` |

## Result

```text
test_envs/reports/results/pytest/test_cases/<test-id>/
├── <execution-id>_result.json
└── <execution-id>_test.log
```

| Result field | Source |
|---|---|
| Test ID | Test case marker |
| Category | Test case marker |
| Fixture configs | `FIXTURE_META` snapshot |
| Test mode | Effective Fixture mode |
| Metrics | `ct_result.metrics` |
| Statistics | `ct_result.statistics` |

## Local LLM

| Item | Rule |
|---|---|
| Usage | Enabled |
| Model | `config.json → ollama.selected_model` |
| Prompt priority | Test `test_prompt` → `ollama.default_prompt` |
| Log | `reports/local_llm/<execution-id>_local_llm.log` |

| Warning count | Severity |
|---:|---|
| 0–1 | `LOW` |
| 2–3 | `MEDIUM` |
| 4–5 | `HIGH` |
| 6+ | `CRITICAL` |

## Markdown

```text
test_envs/reports/markdown/<test-id>/<execution-id>_result.md
docs/tests/pytest/<test-id>__<execution-id>.md
docs/tests/pytest/<test-id>.md
```

## Report generation

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.test_result --pending --docs
```

| Output | Rule |
|---|---|
| Canonical Markdown | Execution ID |
| Latest TEST page | TEST ID |
| Test History | TEST ID execution list |
| Pytest index | Automatic |

## Documents

| Scope | Document |
|---|---|
| pytest | [pytest.md](pytest.md) |
| HIL / Mock | [hil_mock.md](hil_mock.md) |
| Results | [tests/pytest/index.md](tests/pytest/index.md) |
