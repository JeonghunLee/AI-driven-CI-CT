# Pytest Operation

## Identifier

<br/>

| Identifier | Rule | Format |
|---|---|---|
| TEST ID | Required | `CT-<TARGET>-<NNN>` |
| Fixture ID | Required | `FIXTURE-<NNN>` |
| Execution ID | Required | `YYYYMMDD_HHMMSS_ffffff` |

<br/>

## Runtime

<br/>

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

<br/>

## Structure

<br/>

```text
test_envs/tests/pytest/
├── test_cases/
├── fixtures/
├── test_interfaces/{usb,uart,jtag,network}/{mock,hil}/
├── test_equipments/{fpga,saleae,digilent}/{mock,hil}/
└── conftest.py
```

<br/>

## Mode

<br/>

| Priority | Source |
|---:|---|
| 1 | CLI `--fixture-mode=mock|hil` |
| 2 | Marker `fixture_mode` |

<br/>

| Validation | Source |
|---|---|
| Mode enabled | `FIXTURE_META.modes.<mode>.enabled` |
| Interface | `FIXTURE_META.interfaces` |
| Equipment | `FIXTURE_META.equipments` |

<br/>

## Result

<br/>

```text
test_envs/reports/results/pytest/test_cases/<test-id>/
├── <execution-id>_result.json
└── <execution-id>_test.log
```

<br/>

| Result field | Source |
|---|---|
| Test ID | Test case marker |
| Category | Test case marker |
| Fixture configs | `FIXTURE_META` snapshot |
| Test mode | Effective Fixture mode |
| Metrics | `ct_result.metrics` |
| Statistics | `ct_result.statistics` |

## Local LLM

<br/>

| Item | Rule |
|---|---|
| Usage | Enabled |
| Model | `config.json → ollama.selected_model` |
| Prompt priority | Test `test_prompt` → `ollama.default_prompt` |
| Log | `reports/local_llm/<execution-id>_local_llm.log` |

<br/>

| Warning count | Severity |
|---:|---|
| 0–1 | `LOW` |
| 2–3 | `MEDIUM` |
| 4–5 | `HIGH` |
| 6+ | `CRITICAL` |

<br/>

## Markdown

<br/>

```text
test_envs/reports/markdown/<test-id>/<execution-id>_result.md
docs/tests/pytest/<test-id>__<execution-id>.md
docs/tests/pytest/<test-id>.md
```
<br/>

## Report generation

<br/>

```powershell
.\.venv\Scripts\python.exe -m test_envs.tools.test_result --pending --docs
```

<br/>

| Output | Rule |
|---|---|
| Canonical Markdown | Execution ID |
| Latest TEST page | TEST ID |
| Test History | TEST ID execution list |
| Pytest index | Automatic |

<br/>

## Documents

<br/>

| Scope | Document |
|---|---|
| pytest (HIL or Mock) | [pytest.md](pytest.md) |
| Results | [tests/pytest/index.md](tests/pytest/index.md) |

<br/>