# CT-UART-001 Test Result

## Test summary

- **Description:** test_uart_timing
- **Category:** timing
- **Environment:** local
- **Configuration:** {'category': 'timing', 'fixture_id': 'FIXTURE-001', 'fixture_mode': 'mock', 'interface': 'UART', 'equipment': 'Saleae'}
- **Test mode:** mock
- **Equipment:** Saleae
- **Equipment mode:** mock
- **Interface:** UART
- **Interface mode:** mock
- **Result:** **PASS**
- **Execution time:** 0.001 seconds
- **Execution date:** 2026-08-18T04:04:01.493533+00:00
- **Execution ID:** `20260818_040401_493506`

## Test Source

| Item | Value |
|---|---|
| Commit | `ddeca593ac3567e182612ed095f754c240220bd0` |
| Branch | `main` |

## Measurement

- **expected_baudrate:** 921600
- **measured_baudrate:** 921596.667
- **error:** 3.6168981481902543e-06
- **jitter:** 0.00021701388888888888

## Statistics

- **mean:** 921596.6666666666
- **median:** 921602.5
- **min:** 921490.0
- **max:** 921690.0
- **stddev:** 67.55656066503748

## Important logs

- None

## Warnings

- None

## Local LLM analysis

CT-UART-001 passed in 0.001s.

- **Classification:** `passed`
- **Confidence:** 1.00
- **Analyzer:** `deterministic-fallback`

### Failure analysis

Not applicable

### Source review

Not requested

## Test History

| Date | Time | Execution ID | Commit | Branch | Result | Duration (s) | Environment |
|---|---|---|---|---|---|---:|---|
| 2026-08-18 | 04:04:01.493533+00:00 | [20260818_040401_493506](CT-UART-001__20260818_040401_493506.md) | ddeca59 | main | PASS | 0.001 | local |
| 2026-08-18 | 03:01:37.727119+00:00 | [20260818_030137_727071](CT-UART-001__20260818_030137_727071.md) | 33bd0ee | main | PASS | 0.001 | local |
| 2026-08-13 | 07:47:38.432406+00:00 | [20260813-074738-432387](CT-UART-001__20260813-074738-432387.md) | local | unknown | PASS | 0.001 | local |
| 2026-08-13 | 06:54:50.655858+00:00 | [20260813-065450-655846](CT-UART-001__20260813-065450-655846.md) | local | unknown | PASS | 0.000 | local |
| 2026-08-13 | 06:48:38.485012+00:00 | [20260813-064838-484993](CT-UART-001__20260813-064838-484993.md) | local | unknown | PASS | 0.001 | local |
| 2026-08-13 | 06:02:42.833947+00:00 | [20260813-060242-833931](CT-UART-001__20260813-060242-833931.md) | local | unknown | PASS | 0.000 | local |
| 2026-08-13 | 02:40:05.771857+00:00 | [20260813-024005-771843](CT-UART-001__20260813-024005-771843.md) | local | unknown | PASS | 0.000 | local |
| 2026-08-13 | 02:32:02.059339+00:00 | [20260813-023202-059324](CT-UART-001__20260813-023202-059324.md) | local | unknown | PASS | 0.000 | local |
| 2026-08-13 | 01:50:49.885000+00:00 | [20260813-015049-884986](CT-UART-001__20260813-015049-884986.md) | local | unknown | PASS | 0.001 | local |
| 2026-08-13 | 01:49:19.691962+00:00 | [20260813-014919-691948](CT-UART-001__20260813-014919-691948.md) | local | unknown | PASS | 0.000 | local |
| 2026-08-13 | 00:43:23.383204+00:00 | [20260813-004323-383189](CT-UART-001__20260813-004323-383189.md) | local | unknown | PASS | 0.001 | local |
| 2026-08-13 | 00:10:38.341685+00:00 | [20260813-001038-341669](CT-UART-001__20260813-001038-341669.md) | local | unknown | PASS | 0.001 | local |
| 2026-08-13 | 00:07:35.891993+00:00 | [20260813-000735-891978](CT-UART-001__20260813-000735-891978.md) | local | unknown | PASS | 0.000 | local |
