# CT-UART-001 Test Result

## Test summary

| Item | Value |
|---|---|
| Description | test_uart_timing |
| Category | timing |
| Environment | local |
| Result | PASS |
| Execution time | 0.001 seconds |
| Execution date | 2026-08-18T15:42:39.380143+09:00 |
| Execution ID | 20260818_154239_380041 |

### Test configs

| Item | Value |
|---|---|
| Category | timing |
| Fixture ID | FIXTURE-001 |
| Fixture mode | mock |
| Test mode | mock |
| Equipment | Saleae |
| Equipment mode | mock |
| Interface | UART |
| Interface mode | mock |

### Test Source

| Item | Value |
|---|---|
| Commit | f8b4f74c10877a0dd859c5f444480b57ac137a29 |
| Branch | main |

### Measurement

| Item | Value |
|---|---|
| expected_baudrate | 921600 |
| measured_baudrate | 921596.667 |
| error | 3.6168981481902543e-06 |
| jitter | 0.00021701388888888888 |

### Statistics

| Item | Value |
|---|---|
| mean | 921596.6666666666 |
| median | 921602.5 |
| min | 921490.0 |
| max | 921690.0 |
| stddev | 67.55656066503748 |

### Logs

| Item | Value |
|---|---|
| Test log | 20260818_154239_380041_test.log |
| Important | None |

## Local LLM analysis

| Item | Value |
|---|---|
| Classification | Pass |
| Confidence | 0.95 |
| Analyzer | ollama/deepseek-r1:7b |
| working | on |

### LLM Prompt

result.json 분석

### LLM Review

| Item | Value |
|---|---|
| Summary | All tests passed with minimal timing discrepancies. |
| Failure analysis | Not applicable |
| Source review | Not requested |
| Warnings | None |
| Needs escalation | off |

## Test History

| Date | Time | Execution ID | Commit | Branch | Result | Duration (s) | Environment |
|---|---|---|---|---|---|---:|---|
| 2026-08-18 | 15:42:39.380143+09:00 | [20260818_154239_380041](CT-UART-001__20260818_154239_380041.md) | f8b4f74 | main | PASS | 0.001 | local |
| 2026-08-18 | 15:38:43.343459+09:00 | [20260818_153843_343352](CT-UART-001__20260818_153843_343352.md) | 31a3aa2 | main | PASS | 0.001 | local |
| 2026-08-18 | 15:36:58.921402+09:00 | [20260818_153658_921304](CT-UART-001__20260818_153658_921304.md) | 0501967 | main | PASS | 0.000 | local |
| 2026-08-18 | 15:36:45.023008+09:00 | [20260818_153645_022911](CT-UART-001__20260818_153645_022911.md) | 0501967 | main | PASS | 0.000 | local |
| 2026-08-18 | 15:36:21.075599+09:00 | [20260818_153621_075466](CT-UART-001__20260818_153621_075466.md) | 0501967 | main | PASS | 0.000 | local |
| 2026-08-18 | 15:18:45.688737+09:00 | [20260818_151845_688646](CT-UART-001__20260818_151845_688646.md) | a51f1d4 | main | PASS | 0.000 | local |
| 2026-08-18 | 15:18:00.193731+09:00 | [20260818_151800_193627](CT-UART-001__20260818_151800_193627.md) | a51f1d4 | main | PASS | 0.000 | local |
| 2026-08-18 | 15:16:56.950743+09:00 | [20260818_151656_950645](CT-UART-001__20260818_151656_950645.md) | a51f1d4 | main | PASS | 0.000 | local |
| 2026-08-18 | 15:16:36.220726+09:00 | [20260818_151636_220637](CT-UART-001__20260818_151636_220637.md) | a51f1d4 | main | PASS | 0.000 | local |
| 2026-08-18 | 14:52:39.800141+09:00 | [20260818_145239_800032](CT-UART-001__20260818_145239_800032.md) | 9ebc289 | main | PASS | 0.001 | local |
| 2026-08-18 | 14:39:17.419249+09:00 | [20260818_143917_419150](CT-UART-001__20260818_143917_419150.md) | 54ffa7d | main | PASS | 0.001 | local |
| 2026-08-18 | 14:36:34.925452+09:00 | [20260818_143634_925356](CT-UART-001__20260818_143634_925356.md) | ee3794c | main | PASS | 0.000 | local |
| 2026-08-18 | 14:30:00.730977+09:00 | [20260818_143000_730890](CT-UART-001__20260818_143000_730890.md) | 19c3b95 | main | PASS | 0.001 | local |
| 2026-08-18 | 04:49:04.884511+00:00 | [20260818_044904_884486](CT-UART-001__20260818_044904_884486.md) | 9d6d0e0 | main | PASS | 0.000 | local |
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
