# AI-driven Continuous Testing Architecture

## 1. Overview

이 프로젝트는 **VS Code + Python `.venv` 기반의 개발/테스트 환경**을 중심으로 구성한다.

Continuous Testing(CT)은 특정 CI 서버나 Runner 자체를 의미하지 않는다.  
각 개발/실행 환경에서 테스트를 수행하고, 결과와 로그를 분석한 뒤 Markdown으로 기록하여 **MkDocs와 Pandoc을 통해 문서화하는 흐름**을 CT의 핵심으로 정의한다.

핵심 구성은 다음과 같다.

- VS Code
- Python `.venv`
- VS Code Testing
- VS Code Run and Debug
- unittest
- pytest
- Test Equipment
- Test Interfaces
- Ollama + DeepSeek
- Codex
- Markdown
- MkDocs
- Pandoc
- GitHub
- GitHub Actions
- Optional Self-hosted Runner

---

## 2. Overall Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                           VS Code                            │
│                                                              │
│   ┌────────────────┐   ┌────────────────┐   ┌─────────────┐ │
│   │    Testing     │   │ Run and Debug  │   │  AI Agent   │ │
│   │                │   │                │   │             │ │
│   │ unittest       │   │ App / Tool     │   │ Ollama      │ │
│   │ pytest         │   │ Interface      │   │   ↓         │ │
│   │ Run / Debug    │   │ Breakpoint     │   │ DeepSeek    │ │
│   └───────┬────────┘   └───────┬────────┘   └──────┬──────┘ │
│           │                    │                   │         │
│           └────────────────────┼───────────────────┘         │
│                                │                             │
│                             .venv                            │
│                 Python Execution Environment                 │
└────────────────────────────────┼─────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────┐
│                    Continuous Testing                        │
│                                                              │
│   ┌─────────────────────┐      ┌──────────────────────────┐  │
│   │      Unit Test      │      │        pytest / CT       │  │
│   │                     │      │                          │  │
│   │ Python              │      │ Test Cases               │  │
│   │ C / C++             │      │  ├─ Communication        │  │
│   │ Firmware            │      │  ├─ Timing               │  │
│   │ Mock                │      │  ├─ Functional           │  │
│   └─────────────────────┘      │  ├─ Performance          │  │
│                                │  ├─ Stability            │  │
│                                │  └─ Regression           │  │
│                                │                          │  │
│                                │ Test Equipment           │  │
│                                │  ├─ FPGA                 │  │
│                                │  ├─ Saleae               │  │
│                                │  └─ Digilent             │  │
│                                │                          │  │
│                                │ Test Interfaces          │  │
│                                │  ├─ USB                  │  │
│                                │  ├─ UART                 │  │
│                                │  ├─ JTAG                 │  │
│                                │  └─ Network              │  │
│                                └────────────┬─────────────┘  │
└─────────────────────────────────────────────┼────────────────┘
                                              │
                                              ▼
                                  ┌──────────────────────┐
                                  │ Test Execution Data  │
                                  │                      │
                                  │ PASS / FAIL          │
                                  │ Measurement          │
                                  │ stdout / stderr      │
                                  │ Equipment Log        │
                                  │ Interface Log        │
                                  │ Warning              │
                                  └──────────┬───────────┘
                                             │
                                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  Ollama + DeepSeek                           │
│                                                              │
│   DeepSeek 역할                                              │
│                                                              │
│   ├─ TEST Analysis                                           │
│   ├─ Log Analysis                                            │
│   ├─ Source Review                                           │
│   ├─ Warning Analysis                                        │
│   └─ TEST Result Documentation                               │
│                                                              │
│             복잡한 수정 / Root Cause가 필요한 경우            │
│                            │                                 │
│                            ▼                                 │
│                          Codex                               │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
                    ┌───────────────────┐
                    │     Markdown      │
                    │                   │
                    │   Test Result     │
                    │   Log Summary     │
                    │   Warning         │
                    │   Analysis        │
                    │   Source Review   │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼──────────────┐
                │             │              │
                ▼             ▼              ▼
           ┌─────────┐   ┌─────────┐    ┌──────────┐
           │ MkDocs  │   │ Pandoc  │    │  GitHub  │
           │         │   │         │    │  Issue   │
           │ Web Doc │   │ DOCX    │    │ Result   │
           │ History │   │ PDF     │    │ Summary  │
           │ Report  │   │ HTML    │    │          │
           └─────────┘   └─────────┘    └──────────┘
```

---

## 3. VS Code 중심 개발 환경

VS Code를 Local Development 및 Test Front-end로 사용한다.

### 3.1 VS Code Testing

VS Code Testing / Test Explorer는 다음 용도로 사용한다.

- unittest 검색 및 실행
- pytest 검색 및 실행
- 개별 Test Case 실행
- Test Result 확인
- Test Debug
- 실패 Test 재실행
- Test Coverage 확인

```text
VS Code Testing
├─ unittest
└─ pytest
   ├─ communication
   ├─ timing
   ├─ functional
   ├─ performance
   ├─ stability
   └─ regression
```

### 3.2 Run and Debug

VS Code Run and Debug는 Test 자체보다 다음 개발/디버깅에 사용한다.

- Application Debug
- Test Tool Debug
- Test Interface Debug
- Equipment Controller Debug
- Breakpoint
- Variable Inspection
- Call Stack 확인
- UART / USB / JTAG / Network 제어 프로그램 디버깅

```text
Run and Debug
├─ Application
├─ Test Tool
├─ Equipment Controller
└─ Test Interface
```

---

## 4. Python `.venv`

모든 Python 관련 도구와 테스트는 프로젝트 Local `.venv`를 사용한다.

System Python은 가급적 `.venv` 생성 용도로만 사용하고, 실제 Python 실행은 `.venv` 내부 Interpreter를 사용한다.

```text
System Python
     │
     ▼
python -m venv .venv
     │
     ▼
.venv
├─ unittest
├─ pytest
├─ pyserial
├─ pyusb
├─ requests
├─ MkDocs
├─ Report Tools
└─ Ollama Integration Scripts
```

VS Code의 다음 기능도 모두 동일한 `.venv`를 사용하도록 한다.

- Python Interpreter
- Testing
- Run and Debug
- pytest
- unittest
- Report Generator
- MkDocs
- Ollama Integration Script

---

## 5. Test Architecture

테스트는 크게 두 영역으로 구성한다.

```text
tests/
├── unittest/
└── pytest/
```

---

## 6. Unit Test

Unit Test는 Software 자체의 단위 검증을 담당한다.

```text
tests/
└── unittest/
    ├── python/
    ├── c_cpp/
    ├── firmware/
    └── common/
```

주요 목적:

- Function Test
- Class Test
- Module Test
- Algorithm Test
- Mock Test
- Hardware-independent Test

Python에만 한정하지 않고 C/C++ 및 Firmware Test까지 확장 가능한 구조로 유지한다.

---

## 7. pytest / Continuous Testing

pytest는 Integration, Functional, Hardware/Interface 기반 Test를 담당한다.

```text
tests/
└── pytest/
    ├── test_cases/
    ├── test_equipments/
    └── test_interfaces/
```

### 7.1 Test Cases

```text
test_cases/
├── communication/
├── timing/
├── functional/
├── performance/
├── stability/
└── regression/
```

Test Case에는 실제 Test Logic을 작성한다.

Equipment 연결이나 Interface 초기화 코드는 Test Case와 분리한다.

### 7.2 Test Equipment

```text
test_equipments/
├── fpga/
├── saleae/
└── digilent/
```

역할:

- FPGA
  - DUT
  - Pattern Generator
  - Protocol Generator
  - Frame Generator
  - Timing Generator
- Saleae
  - Protocol Capture
  - Timing Measurement
  - UART/SPI Analysis
  - Jitter Analysis
- Digilent
  - Voltage
  - Waveform
  - Power Sequence
  - Analog/Digital Measurement

### 7.3 Test Interfaces

```text
test_interfaces/
├── usb/
├── uart/
├── jtag/
└── network/
```

지원 Interface:

- USB
- UART
- JTAG
- Network

대표 구현:

- UART → pyserial
- USB → PyUSB / Vendor API
- JTAG → OpenOCD / Vendor CLI / API
- Network → socket / HTTP / SSH / TCP / UDP

---

## 8. Test Equipment와 Test Interface 분리

Test Equipment는 **무엇으로 측정하거나 제어하는가**를 의미한다.

Test Interface는 **어떻게 DUT와 통신하는가**를 의미한다.

예를 들어 UART Timing Test:

```text
             pytest Test Case
                    │
        ┌───────────┴───────────┐
        │                       │
 Test Interface          Test Equipment
        │                       │
       UART                   Saleae
        │                       │
        └────────► DUT ◄────────┘
```

UART를 이용해 DUT를 제어하고, Saleae를 이용해 실제 신호를 측정한다.

---

## 9. Test Result / Log / Measurement

각 Test 실행은 최소 다음 세 종류의 데이터를 생성한다.

```text
Test Execution
├─ Result
├─ Log
└─ Measurement
```

### Result

- PASS / FAIL
- Test ID
- Execution Time
- Environment
- Commit
- Configuration

### Log

- stdout
- stderr
- Test Log
- Equipment Log
- Interface Log
- Warning
- Error / Stack Trace

### Measurement

예:

- Timing
- Latency
- Jitter
- Throughput
- Baudrate
- Voltage
- Frequency
- Packet Loss
- CRC Error

---

## 10. DeepSeek 역할

Ollama를 Local LLM Runtime으로 사용하고, **DeepSeek를 Primary Local LLM Model**로 사용한다.

DeepSeek는 다음 다섯 가지 역할을 담당한다.

```text
Ollama Runtime
└── DeepSeek
    ├── TEST Analysis
    ├── Log Analysis
    ├── Source Review
    ├── Warning Analysis
    └── TEST Result Documentation
```

### TEST Analysis

- unittest / pytest 결과 분석
- PASS / FAIL 분석
- 실패 Pattern 분석
- Regression 여부 판단 보조

### Log Analysis

- Error 추출
- Warning 추출
- Stack Trace 분석
- 반복 Error Pattern 분석
- Equipment / Interface Log 분석

### Source Review

- 변경 Source Review
- 잠재 Bug 분석
- 예외 처리 누락 분석
- Test Coverage 누락 분석
- 코드 위험 요소 분석

### Warning Analysis

- Compiler Warning
- pytest Warning
- Runtime Warning
- Static Analysis Warning

Warning을 중요도에 따라 분류할 수 있도록 한다.

예:

```text
Critical
Important
Low
```

### TEST Result Documentation

DeepSeek는 Test Result와 Log 분석 결과를 Markdown으로 정리한다.

주요 내용:

- Test Summary
- Test Configuration
- PASS / FAIL
- Measurement
- Statistics
- Important Log
- Warning
- Failure Analysis
- Source Review
- AI Summary

---

## 11. Codex 역할

Codex는 기본 분석 도구가 아니라 **Escalation Agent**로 사용한다.

DeepSeek에서 처리하기 어려운 경우에만 사용한다.

```text
DeepSeek
   │
   ├─ 해결 가능 → 완료
   │
   └─ 복잡한 문제
           │
           ▼
         Codex
```

Codex 사용 대상:

- 복잡한 Root Cause Analysis
- Multi-file Code Modification
- Refactoring
- Architecture 변경
- 복잡한 Test Case 생성
- Source Code Fix
- DeepSeek가 해결하지 못한 문제

목표는 **DeepSeek를 적극 활용하여 Codex 사용량을 최소화하는 것**이다.

---

## 12. Markdown-first Documentation

CT 결과의 사람이 읽는 기본 문서 포맷은 Markdown으로 한다.

```text
Test
 ↓
Result + Log + Measurement
 ↓
DeepSeek Analysis
 ↓
Markdown
```

예:

```text
reports/
└── CT-UART-001/
    ├── result.md
    ├── test.log
    ├── stdout.log
    ├── stderr.log
    └── measurement.csv
```

`result.md`에는 다음 정보를 기록한다.

- Test ID
- Test Description
- Test Environment
- Test Equipment
- Test Interface
- Test Result
- PASS / FAIL
- Measurement
- Statistics
- Important Logs
- Warnings
- DeepSeek Analysis
- Source Review
- Commit / Revision
- Execution Date

---

## 13. MkDocs

MkDocs는 Markdown Test Result를 Web Documentation으로 제공한다.

```text
Markdown
   │
   ▼
MkDocs
   │
   ├─ Test Report
   ├─ Test History
   ├─ Regression History
   └─ Searchable Documentation
```

예:

```text
docs/
└── test/
    ├── index.md
    ├── unit/
    └── ct/
        ├── communication/
        ├── timing/
        ├── functional/
        ├── performance/
        ├── stability/
        └── regression/
```

---

## 14. Pandoc

Pandoc은 Markdown Test Result를 공식 문서 포맷으로 변환하는 데 사용한다.

```text
result.md
   │
   └── Pandoc
         ├─ DOCX
         ├─ PDF
         └─ HTML
```

즉 하나의 Markdown 결과를 기준으로 Web 문서와 제출 문서를 모두 생성할 수 있도록 한다.

---

## 15. GitHub Issue

GitHub Issue는 복잡한 Test 문서 작성 도구가 아니라 **Test 설정 및 결과 확인 UI**로 사용한다.

사용자는 Issue에서 필요한 설정만 선택한다.

예:

```text
Test Type
├─ Unit Test
└─ pytest / CT

Test Category
├─ Communication
├─ Timing
├─ Functional
├─ Performance
├─ Stability
└─ Regression

Test Equipment
├─ None
├─ FPGA
├─ Saleae
└─ Digilent

Test Interface
├─ None
├─ USB
├─ UART
├─ JTAG
└─ Network

Test Function
├─ Connection
├─ Read / Write
├─ Timing
├─ Throughput
├─ Latency
├─ Stability
└─ Custom
```

Test 완료 후 Issue에는 핵심 결과를 기록한다.

- PASS / FAIL
- 주요 Measurement
- Warning Summary
- DeepSeek Summary
- MkDocs 문서 위치
- Raw Log / Artifact 위치

Raw Log 전체를 Issue에 붙이지 않는다.

---

## 16. GitHub Automation Layer

GitHub Actions는 CT 그 자체가 아니라 **자동 실행을 위한 Orchestration Layer**로 사용한다.

```text
GitHub
├─ Repository
├─ Issue
├─ Pull Request
└─ GitHub Actions
```

GitHub-hosted Runner를 일반 자동화에 사용할 수 있다.

Self-hosted Runner는 Optional로 둔다.

---

## 17. Optional Self-hosted Runner

Self-hosted Runner는 필수 요소가 아니다.

주로 다음과 같은 CI/CD 또는 특수 환경 자동화가 필요한 경우 사용한다.

- 특정 Compiler / SDK
- Vendor Tool
- Firmware Build
- Package
- Deploy
- 내부 Network
- 특정 USB/JTAG 장비 접근
- Machine-specific Environment

```text
GitHub Actions
      │
      ├─ GitHub-hosted Runner
      │      └─ General CI / Test
      │
      └─ Self-hosted Runner
             └─ Optional CI/CD / Special Environment
```

즉:

```text
CT = Test + Analysis + Documentation

Self-hosted Runner = Optional Execution Environment
```

---

## 18. VS Code Project Configuration

프로젝트에는 VS Code 설정을 포함한다.

```text
.vscode/
├── settings.json
├── launch.json
└── tasks.json
```

### settings.json

주요 목적:

- `.venv` Python Interpreter
- pytest discovery
- unittest / pytest 설정
- Testing 연동

### launch.json

주요 목적:

- Run and Debug
- Application Debug
- Test Tool Debug
- Equipment Controller Debug
- Interface Debug

### tasks.json

주요 목적:

- 반복적인 Test 실행
- pytest Command
- MkDocs Build
- Pandoc Build
- Report Generation
- Tool 실행

---

## 19. Recommended Repository Structure

```text
.
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── test.yml
│   │   └── config.yml
│   └── workflows/
│
├── .venv/
│
├── tests/
│   ├── unittest/
│   │   ├── python/
│   │   ├── c_cpp/
│   │   ├── firmware/
│   │   └── common/
│   │
│   └── pytest/
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
│   ├── log_parser/
│   ├── deepseek/
│   ├── github_reporter/
│   ├── mkdocs_reporter/
│   └── pandoc_reporter/
│
├── reports/
│   ├── logs/
│   ├── measurements/
│   └── markdown/
│
├── docs/
│   └── test/
│
├── mkdocs.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

`.venv/`는 Local Runtime Directory이며 Git에는 포함하지 않는다.

`.gitignore`에 반드시 추가한다.

```text
.venv/
```

---

## 20. Final Workflow

```text
VS Code
  │
  ├─ Testing
  ├─ Run and Debug
  └─ AI Agent
       │
       ▼
     .venv
       │
       ▼
unittest / pytest
       │
       ▼
Test Result
+ Log
+ Measurement
+ Warning
       │
       ▼
Ollama + DeepSeek
       │
       ├─ TEST Analysis
       ├─ Log Analysis
       ├─ Source Review
       ├─ Warning Analysis
       └─ TEST Result Documentation
       │
       ▼
    Markdown
       │
 ┌─────┼────────────┐
 ▼     ▼            ▼
MkDocs Pandoc    GitHub Issue
 │      │
Web    DOCX/PDF
Docs

복잡한 문제
     │
     ▼
   Codex
```

---

## 21. Core Principles

1. VS Code를 Local Development 및 Test Front-end로 사용한다.
2. 모든 Python 실행은 프로젝트 `.venv`를 사용한다.
3. VS Code Testing과 Run and Debug를 적극 활용한다.
4. Unit Test와 pytest CT를 분리한다.
5. Test Equipment와 Test Interface를 분리한다.
6. CT는 특정 Runner나 CI Server에 종속되지 않는다.
7. DeepSeek를 Test / Log / Warning / Source Review / Documentation의 Primary LLM으로 사용한다.
8. Ollama를 DeepSeek의 Local Runtime으로 사용한다.
9. Codex는 복잡한 문제 해결용 Escalation Agent로 사용한다.
10. Test 결과는 Markdown-first 방식으로 기록한다.
11. MkDocs는 Web Documentation을 담당한다.
12. Pandoc은 DOCX/PDF/HTML 문서 생성을 담당한다.
13. GitHub Issue는 Test 설정과 핵심 결과 확인에 사용한다.
14. GitHub Actions는 자동 실행용 Orchestration Layer로만 사용한다.
15. Self-hosted Runner는 CI/CD 또는 특수 환경 실행이 필요한 경우에만 Optional로 사용한다.

---

## 22. Architecture Summary

> **VS Code-centered Continuous Testing using project-local Python venv, VS Code Testing and Run and Debug, DeepSeek-assisted test/log/source/warning analysis, Markdown-first documentation, MkDocs/Pandoc reporting, and optional GitHub automation.**
