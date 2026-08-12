GitHub 기반의 **AI-driven CI/CT 자동화 시스템**을 구성해줘.

핵심 목표는 다음과 같다.

* GitHub를 전체 테스트 자동화의 중심으로 사용한다.
* GitHub Actions + Self-hosted Runner 기반으로 테스트를 실행한다.
* Windows/Linux Self-hosted Runner를 모두 지원 가능한 구조로 만든다.
* 테스트는 **Unit Test와 pytest 기반 CT**로 구분한다.
* pytest CT는 **Test Equipment와 Test Interface**를 분리한다.
* AI는 **Ollama + Codex** 두 계층으로 구성한다.
* **Codex 사용량을 줄이기 위해 Ollama를 우선 사용한다.**
* GitHub Issue는 사용자가 Test 설정을 선택하고 결과를 받는 UI로 사용한다.
* Test Result, Measurement, Log를 모두 저장한다.
* Test 결과는 GitHub Issue와 MkDocs에 자동 반영한다.
* Raw Log와 Measurement 파일은 GitHub Actions Artifact로 보존한다.
* Jenkins와 Continue는 사용하지 않는다.

---

# 1. Overall Architecture

전체 구조는 다음을 기준으로 한다.

```text id="8wprcq"
                    Developer
                        │
                        ▼
                     GitHub
             ┌──────────┼───────────┐
             │          │           │
         Repository    Issue        PR
                        │
                        ▼
                 GitHub Actions
                        │
                        ▼
                Self-hosted Runner
                        │
             ┌──────────┴───────────┐
             │                      │
         Unit Test              pytest / CT
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
              Test Equipment                Test Interface
                     │                             │
            FPGA / Saleae / Digilent       USB/UART/JTAG/Network
                     │                             │
                     └─────────────┬───────────────┘
                                   ▼
                                  DUT
                                   │
                                   ▼
                              Test Result
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                      result.json          Raw Log
                         │                   │
                         └─────────┬─────────┘
                                   ▼
                                Ollama
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
               GitHub Issue      MkDocs         Artifact
                    │
                    │ Complex Failure
                    ▼
                  Codex
```

---

# 2. AI Architecture

두 개의 AI 계층을 사용한다.

## Ollama

Ollama를 **Default / Primary AI**로 사용한다.

목적은 Codex 사용량을 줄이는 것이다.

Ollama가 우선 수행할 작업:

* Test Result 분석
* Raw Log 분석
* Error / Warning 추출
* PASS / FAIL Summary
* Failure Classification
* Markdown 생성
* GitHub Issue Result 생성
* MkDocs Test Report 생성
* 반복적인 Test Code 생성
* 간단한 코드 분석
* 기존 Test History 비교
* Regression Pattern 분석
* Local/private processing

기본 정책:

```text id="autb7x"
Task
 │
 ▼
Ollama
 │
 ├── 해결 가능 ───────► 완료
 │
 └── 해결 불가능
           │
           ▼
         Codex
```

---

## Codex

Codex는 **Escalation Agent**로 사용한다.

다음 경우에만 Codex를 사용한다.

* 복잡한 Source Code 분석
* 여러 Source File 수정
* Root Cause Analysis
* Architecture 변경
* 복잡한 Test Case 생성
* Refactoring
* 반복 Failure
* Ollama confidence가 낮은 경우
* Ollama가 원인을 판단하지 못한 경우

즉:

```text id="w3w0mg"
Ollama = Default AI
Codex  = Advanced / Escalation AI
```

---

# 3. GitHub 기반 구조

GitHub를 Single Source of Truth로 사용한다.

사용 항목:

```text id="n691c5"
GitHub
├── Repository
├── Issue
├── Pull Request
├── GitHub Actions
├── Self-hosted Runner
├── Artifact
└── Test History
```

별도의 Jenkins 서버는 사용하지 않는다.

---

# 4. Test Architecture

Test는 크게 두 영역으로 분리한다.

```text id="oi15om"
tests/
├── unittest/
└── pytest/
```

---

# 5. Unit Test

Unit Test 영역은 Python뿐만 아니라 다른 Software/Firmware까지 확장 가능하게 한다.

```text id="h6pbwk"
tests/
└── unittest/
    ├── python/
    ├── c_cpp/
    ├── firmware/
    └── common/
```

목적:

* Function Test
* Class Test
* Module Test
* Algorithm Test
* Mock Test
* Hardware-independent Test

---

# 6. pytest / Continuous Testing

pytest는 Integration / Functional / Hardware CT를 담당한다.

다음 세 영역으로 나눈다.

```text id="db4mta"
tests/
└── pytest/
    ├── test_cases/
    ├── test_equipments/
    └── test_interfaces/
```

---

# 7. Test Cases

실제 Test Scenario는 별도 관리한다.

```text id="ow2b3i"
test_cases/
├── communication/
├── timing/
├── functional/
├── performance/
├── stability/
└── regression/
```

Test Case에는 실제 테스트 Logic만 작성한다.

Equipment 제어 구현이나 Interface 연결 구현을 Test Case 내부에 직접 넣지 않는다.

---

# 8. Test Equipment

외부 측정 장비 또는 Programmable Test Hardware를 관리한다.

```text id="r5r00v"
test_equipments/
├── fpga/
├── saleae/
└── digilent/
```

역할:

### FPGA

```text id="telnvb"
FPGA as DUT
또는
FPGA as Test Equipment
```

예:

* Pattern Generator
* Protocol Generator
* Frame Generator
* Timing Generator

### Saleae

예:

* UART timing
* SPI timing
* Protocol capture
* Jitter
* Signal analysis

### Digilent

예:

* Voltage
* Waveform
* Power sequence
* Analog measurement
* Digital measurement

---

# 9. Test Interface

DUT와 연결하거나 제어하기 위한 Transport / Interface Layer를 분리한다.

```text id="5dd6gw"
test_interfaces/
├── usb/
├── uart/
├── jtag/
└── network/
```

지원:

```text id="cm6ebw"
USB
UART
JTAG
Network
```

구현 예:

* UART → pyserial
* USB → PyUSB / Vendor API
* JTAG → OpenOCD / Vendor CLI/API
* Network → socket / HTTP / SSH / TCP / UDP

가능한 경우 다음과 같은 공통 API를 사용한다.

```python id="6jh8nk"
connect()
disconnect()
read()
write()
execute()
```

단 Interface 특성상 필요하지 않은 API는 억지로 구현하지 않는다.

---

# 10. Equipment와 Interface 분리

예:

UART Timing CT

```text id="jtv72k"
                  pytest
                     │
          ┌──────────┴──────────┐
          │                     │
      Interface              Equipment
          │                     │
         UART                 Saleae
          │                     │
          └────────► DUT ◄──────┘
```

UART로 DUT에 명령을 보내고 Saleae로 실제 UART Signal을 측정한다.

pytest에서 결과를 검증한다.

```python id="8hzlgp"
assert baudrate_error < 0.02
assert jitter < allowed_jitter
```

---

# 11. pytest Fixture

Hardware 및 Interface 초기화는 fixture를 이용한다.

```python id="k7nesv"
@pytest.fixture
def uart():
    interface = UARTInterface(...)
    interface.connect()

    yield interface

    interface.disconnect()
```

```python id="k1wuzm"
@pytest.fixture
def saleae():
    equipment = SaleaeController(...)
    equipment.connect()

    yield equipment

    equipment.disconnect()
```

Test Case에서는 장비 초기화/종료 코드가 최대한 보이지 않게 한다.

---

# 12. GitHub Issue Template

Issue Template은 복잡하게 만들지 않는다.

**하나의 Test Request Issue Form을 기본으로 사용한다.**

```text id="6550ib"
.github/
└── ISSUE_TEMPLATE/
    ├── test.yml
    └── config.yml
```

Issue는 Test Documentation 작성 도구가 아니라 **Test 설정 UI**로 사용한다.

사용자가 선택할 항목:

```text id="3iihvq"
Test Type
├── Unit Test
└── pytest / CT

Test Category
├── Communication
├── Timing
├── Functional
├── Performance
├── Stability
└── Regression

Test Equipment
├── None
├── FPGA
├── Saleae
└── Digilent

Test Interface
├── None
├── USB
├── UART
├── JTAG
└── Network

Test Function
├── Connection
├── Read / Write
├── Timing
├── Throughput
├── Latency
├── Stability
└── Custom

Runner
├── Default
├── Windows
└── Linux
```

필요한 경우에만 추가 입력한다.

```text id="m20k3f"
Target / DUT
Test Parameter
Expected Result
Additional Option
```

---

# 13. Issue 기반 실행

사용자 Workflow는 단순하게 유지한다.

```text id="2ouh30"
Issue 생성
     │
     ▼
Test 항목 선택
     │
     ▼
GitHub Actions
     │
     ▼
Self-hosted Runner
     │
     ▼
Test 실행
     │
     ▼
결과 수신
```

즉 사용자는:

> Issue 생성 → 필요한 Test 설정 선택 → 결과 확인

만 하면 된다.

---

# 14. GitHub Actions

Workflow는 최소 두 개로 구성한다.

```text id="2dc665"
.github/
└── workflows/
    ├── unit-test.yml
    └── continuous-test.yml
```

기본적으로 Self-hosted Runner를 사용한다.

```yaml id="w3qf5j"
runs-on: self-hosted
```

향후 GitHub Runner Label을 이용할 수 있도록 한다.

```yaml id="e6h3x2"
runs-on:
  - self-hosted
  - hw-test
```

필요한 Label 예:

```text id="fdweks"
windows
linux
fpga
saleae
digilent
```

특정 OS나 장비 Label을 초기부터 강제하지 않는다.

---

# 15. Test Output

각 Test 실행에서는 세 종류의 결과를 생성한다.

```text id="f3wn86"
Test
 │
 ├── Result
 ├── Log
 └── Measurement
```

예:

```text id="o22brh"
PASS / FAIL

Log
├── stdout
├── stderr
├── equipment log
└── interface log

Measurement
├── timing
├── latency
├── jitter
├── throughput
└── 기타 측정값
```

---

# 16. Result Normalizer

Test Framework별 결과 형식이 달라도 최종 결과는 표준화한다.

```text id="33c27r"
unittest ─┐
          │
pytest ───┼──► Result Normalizer
          │
Tools ────┘
                │
                ▼
            result.json
```

`result.json`을 Test 결과의 Single Source of Truth로 사용한다.

예:

```json id="ltvhrq"
{
  "test_id": "CT-UART-001",
  "execution_id": "20260812-001",
  "status": "FAIL",
  "category": "timing",
  "duration": 12.42,
  "interface": "UART",
  "equipment": "Saleae",
  "commit": "abcdef1",
  "runner": "hw-runner-01",

  "metrics": {
    "expected_baudrate": 921600,
    "measured_baudrate": 921502,
    "error": 0.00011,
    "jitter": 0.028
  },

  "statistics": {
    "mean": 921510,
    "median": 921520,
    "min": 920900,
    "max": 922100,
    "stddev": 285
  },

  "logs": {
    "main": "test.log",
    "stdout": "stdout.log",
    "stderr": "stderr.log",
    "equipment": "equipment.log"
  }
}
```

---

# 17. Log 관리

각 Test 실행마다 Log를 반드시 보존한다.

```text id="81i8g2"
logs/
└── <test-id>/
    └── <execution-id>/
        ├── test.log
        ├── stdout.log
        ├── stderr.log
        ├── equipment.log
        ├── interface.log
        └── result.json
```

필요하면 추가:

```text id="8zgc44"
measurement.csv
uart.log
usb.log
jtag.log
network.log
saleae.csv
waveform.*
```

---

# 18. GitHub Artifact

Raw Log 및 Measurement Data는 GitHub Actions Artifact로 저장한다.

예:

```text id="x9y2d4"
CT-UART-001-20260812-001/
├── result.json
├── test.log
├── stdout.log
├── stderr.log
├── equipment.log
├── interface.log
└── measurement.csv
```

Test FAIL 여부와 관계없이 Artifact가 저장되도록 한다.

GitHub Actions에서 `if: always()` 또는 동등한 방식으로 구성한다.

---

# 19. Ollama Result Processing

테스트 종료 후 Ollama가 결과를 우선 분석한다.

```text id="89np1a"
result.json
    +
Raw Log
    │
    ▼
  Ollama
    │
    ├── PASS / FAIL Summary
    ├── Error 추출
    ├── Warning 추출
    ├── Failure Classification
    ├── Important Log 추출
    ├── Result Summary
    ├── Issue Comment 생성
    └── MkDocs 생성
```

Raw Log 전체를 LLM에 던지기 전에 프로그램적으로 처리 가능한 정보는 먼저 Parsing한다.

예:

* Timestamp
* Error code
* Warning
* Metric
* Measurement
* Stack Trace

이를 통해 Ollama 처리량도 줄인다.

---

# 20. GitHub Issue Result

Test가 완료되면 기존 Issue에 자동 Comment를 추가한다.

Issue에는 Raw Log 전체를 넣지 않는다.

예:

```text id="z8kvly"
## Test Result

Result: FAIL

Test
- Type: CT
- Category: Timing
- Interface: UART
- Equipment: Saleae

Measurement
- Expected Baudrate: 921600
- Measured Baudrate: 921502
- Error: 0.011 %
- Jitter: 2.8 %

Statistics
- Mean: ...
- Median: ...
- Min: ...
- Max: ...
- Std Dev: ...

Failure
- UART jitter threshold exceeded

AI Analysis
- Ollama generated summary

Logs
- Artifact available
- Detailed MkDocs report available

Commit: abcdef1
Runner: hw-runner-01
Execution ID: 20260812-001
```

즉 Issue에는:

```text id="to43l6"
Test 설정
+
PASS / FAIL
+
주요 Measurement
+
Statistics
+
Log Summary
+
Ollama Analysis
+
Artifact / MkDocs 위치
```

를 보여준다.

---

# 21. MkDocs Test Report

MkDocs는 상세 Test Documentation 및 History를 담당한다.

```text id="s6jqla"
docs/
└── test/
    ├── index.md
    │
    ├── unit/
    │
    └── ct/
        ├── communication/
        ├── timing/
        ├── functional/
        ├── performance/
        ├── stability/
        └── regression/
```

Test Report 예:

```text id="3ow71a"
docs/test/ct/timing/CT-UART-001.md
```

페이지에는 다음을 포함한다.

```text id="qu6dsj"
Test ID
Test Configuration
Test Equipment
Test Interface
Test Parameter
Expected Result
PASS / FAIL

Measurement
Statistics
Execution Time

Important Log
Error / Warning Summary

Ollama Analysis

GitHub Issue
Commit
Runner
Execution ID

Test History
```

---

# 22. Test History

MkDocs에서 Test History도 관리할 수 있도록 한다.

```text id="4sez23"
CT-UART-001
├── Latest Result
├── History
└── Trend
```

최소 기록:

```text id="svwy5r"
Date
Execution ID
Commit
PASS / FAIL
Duration
Mean
Median
Min
Max
Std Dev
Measurement
Runner
Issue
```

향후 Regression 분석이 가능하도록 한다.

---

# 23. Codex Escalation

Ollama에서 다음 조건이 발생한 경우에만 Codex 사용을 고려한다.

```text id="44jlwu"
Ollama
  │
  ├── 해결 가능
  │      └── Done
  │
  └── 해결 불가능
          │
          ▼
        Codex
```

Codex 호출 조건:

```text id="dpjmyn"
Complex Failure
Repeated Failure
Root Cause Unknown
Source Code Fix Required
Multi-module Failure
Architecture Change Required
Developer Explicit Request
```

Codex 사용량 최소화가 설계 목표다.

---

# 24. Repository Structure

최종 Repository 구조는 다음을 기준으로 한다.

```text id="7mihtk"
.
├── .github/
│   │
│   ├── ISSUE_TEMPLATE/
│   │   ├── test.yml
│   │   └── config.yml
│   │
│   └── workflows/
│       ├── unit-test.yml
│       └── continuous-test.yml
│
├── tests/
│   │
│   ├── unittest/
│   │   ├── python/
│   │   ├── c_cpp/
│   │   ├── firmware/
│   │   └── common/
│   │
│   └── pytest/
│       │
│       ├── test_cases/
│       │   ├── communication/
│       │   ├── timing/
│       │   ├── functional/
│       │   ├── performance/
│       │   ├── stability/
│       │   └── regression/
│       │
│       ├── test_equipments/
│       │   ├── fpga/
│       │   ├── saleae/
│       │   └── digilent/
│       │
│       ├── test_interfaces/
│       │   ├── usb/
│       │   ├── uart/
│       │   ├── jtag/
│       │   └── network/
│       │
│       └── conftest.py
│
├── tools/
│   ├── result_normalizer/
│   ├── log_parser/
│   ├── ollama/
│   ├── github_reporter/
│   ├── mkdocs_reporter/
│   └── codex_escalation/
│
├── reports/
│   ├── raw/
│   ├── json/
│   └── logs/
│
├── docs/
│   └── test/
│       ├── index.md
│       ├── unit/
│       └── ct/
│
├── mkdocs.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# 25. Initial Implementation

처음에는 실제 모든 Hardware API를 구현하지 않는다.

다음 순서로 구현한다.

1. Repository Skeleton
2. GitHub Issue Form
3. GitHub Actions Self-hosted Workflow
4. Unit Test Sample
5. pytest Sample
6. Mock UART Interface
7. Mock Saleae Equipment
8. UART Timing Mock CT
9. Result Normalizer
10. `result.json`
11. Logging system
12. Artifact upload
13. Ollama Result Analyzer
14. GitHub Issue Result Reporter
15. MkDocs Report Generator
16. Test History
17. Codex Escalation Interface

---

# 26. Final Workflow

최종 사용자 Workflow는 다음과 같다.

```text id="lbucq5"
GitHub Issue 생성
        │
        ▼
Test 설정 선택
        │
        ▼
GitHub Actions
        │
        ▼
Self-hosted Runner
        │
        ├── Unit Test
        │
        └── pytest / CT
                │
                ▼
        Result + Log + Measurement
                │
                ▼
             result.json
                │
                ▼
              Ollama
                │
       ┌────────┼─────────┐
       ▼        ▼         ▼
    Issue     MkDocs    Artifact
    Result    Report    Raw Logs
       │
       │ Complex Failure
       ▼
     Codex
```

최종 역할은 다음과 같이 정의한다.

* **GitHub Issue** = Test 설정 + 실행 요청 + 핵심 결과
* **GitHub Actions** = CI/CT Orchestration
* **Self-hosted Runner** = 실제 Test 실행
* **unittest** = Software Unit Test
* **pytest** = Integration / Functional / Hardware CT
* **Test Equipment** = FPGA / Saleae / Digilent
* **Test Interface** = USB / UART / JTAG / Network
* **result.json** = Test Result Single Source of Truth
* **Log** = Debug 및 추적을 위한 Raw Evidence
* **GitHub Artifact** = Raw Log / Measurement 저장
* **Ollama** = 기본 AI 분석 및 Report 생성
* **Codex** = 복잡한 분석 및 코드 수정용 Escalation Agent
* **MkDocs** = 상세 Test Report / History / Trend

구조를 과도하게 복잡하게 만들지 말고 **GitHub + Self-hosted Runner + Ollama First + Codex Escalation**이라는 원칙을 유지해줘.
