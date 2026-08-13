# AI-driven Continuous Testing

VS Code와 프로젝트 로컬 Python `.venv`를 중심으로 Unit Test 및 pytest CT를 실행하고, Ollama의 DeepSeek 모델로 결과·로그·경고·소스 변경을 분석한 뒤 Markdown으로 기록하는 프로젝트입니다. Markdown 결과는 MkDocs 웹 문서와 Pandoc DOCX/PDF/HTML 출력의 공통 원본입니다.

상세 설계는 [DESIGN.md](DESIGN.md)를 참고하세요.

## 구성

- VS Code Testing 및 Run and Debug
- 프로젝트 로컬 `.venv`
- Python Unit Test와 확장 가능한 C/C++·Firmware 구조
- pytest 기반 Integration/Functional/Hardware CT
- 분리된 Test Equipment와 Test Interface
- Mock UART 및 Mock Saleae UART Timing CT
- Ollama Runtime + DeepSeek Primary Model
- Markdown-first 결과 및 실행 이력
- MkDocs 게시와 Pandoc 문서 변환
- GitHub-hosted runner 기반 일반 자동화
- 장비/특수 환경용 optional self-hosted runner
- 복잡한 실패를 위한 Codex escalation 판단

## 환경 준비

Windows PowerShell 기준입니다. VS Code의 `Setup: Create Python Virtual Environment` task로도 실행할 수 있습니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

VS Code가 `.venv\Scripts\python.exe`를 선택하면 Test Explorer에서 전체 테스트와 개별 테스트를 실행하거나 디버깅할 수 있습니다.

### VS Code Run and Debug

Run and Debug에는 다음 실행 구성이 있습니다.

1. `Setup 1: Install Python Virtual Environment`: `.venv` 생성 후 `requirements.txt`를 설치합니다.
2. `Setup 2: Install Ollama and DeepSeek`: Ollama가 없으면 OS 패키지 관리자로 설치하고 서버를 시작한 뒤 `deepseek-r1:7b`를 pull합니다.
3. `Run 3: Extension Module`: `main()`을 제공하는 Python 모듈을 실행하는 확장용 진입점입니다.
4. `Test Result: Generate Latest Markdown`: 테스트를 재실행하지 않고 가장 최근 결과로 Markdown을 만듭니다.

확장 실행은 `tools/extensions/example.py`를 새 모듈로 교체하고 `.vscode/launch.json`의 `--module` 값만 변경하면 됩니다.

### VS Code Testing

VS Code Python 확장은 pytest와 unittest를 동시에 활성화하면 pytest만 실행하므로, Test Explorer에서는 pytest adapter가 다음 두 디렉터리를 함께 검색하도록 구성했습니다.

- pytest: `tests/pytest`
- unittest: `tests/unittest`

따라서 Testing 트리에는 `pytest`와 `unittest` 디렉터리가 각각 나타납니다. unittest 코드는 표준 `unittest.TestCase`로 작성되어 있어 Test Explorer의 pytest 실행과 `Test: Run unittest Suite` task의 unittest discovery 양쪽에서 사용할 수 있습니다.

## 테스트와 리포트

```powershell
# 전체 테스트
.\.venv\Scripts\python.exe -m pytest

# CT만 실행
.\.venv\Scripts\python.exe -m pytest tests/pytest -m ct -s

# 최신 실행을 DeepSeek로 분석하고 Markdown 생성
.\.venv\Scripts\python.exe -m test_result

# Markdown을 생성하고 docs/test에도 게시
.\.venv\Scripts\python.exe -m test_result --docs

# 변경 소스도 함께 리뷰
.\.venv\Scripts\python.exe -m test_result --docs --source-review
```

Ollama 기본 주소는 `http://127.0.0.1:11434`, 기본 모델은 `deepseek-r1:7b`입니다.

```powershell
$env:OLLAMA_URL = "http://127.0.0.1:11434"
$env:DEEPSEEK_MODEL = "deepseek-r1:7b"
```

Ollama 또는 DeepSeek가 준비되지 않은 경우에도 규칙 기반 fallback이 테스트 결과와 경고를 Markdown으로 정리합니다.

## 결과 구조

```text
reports/
├── logs/<test-id>/<execution-id>/
│   ├── result.json
│   ├── analysis.json
│   ├── codex-escalation.json
│   ├── test.log
│   ├── stdout.log
│   ├── stderr.log
│   ├── equipment.log
│   └── interface.log
├── measurements/<test-id>/<execution-id>/
│   ├── measurement.json
│   └── measurement.csv
└── markdown/<test-id>/
    ├── latest.md
    └── <execution-id>/result.md
```

사람이 읽는 기준 결과는 `reports/markdown/.../result.md`입니다. JSON은 테스트 실행과 도구 사이의 machine-readable 중간 데이터로만 사용합니다.

`python -m test_result`를 실행하면 이 canonical 보고서를 생성한 뒤 가장 최근 사본을 `test_result/markdown/latest.md`에도 넣습니다.

```text
python -m test_result --docs
├── docs/index.md
└── docs/test/<scope>/<category>/
    ├── <test-id>.md
    └── <test-id>/
        ├── <execution-id-1>.md
        ├── <execution-id-2>.md
        └── <execution-id-N>.md
```

## Pandoc 변환

Pandoc 실행 파일을 별도로 설치하고 PATH에 등록해야 합니다.

```powershell
.\.venv\Scripts\python.exe -m tools.pandoc_reporter --latest --format html
.\.venv\Scripts\python.exe -m tools.pandoc_reporter --latest --format docx
.\.venv\Scripts\python.exe -m tools.pandoc_reporter --latest --format pdf
```

PDF 생성에는 설치 환경에 따라 LaTeX 같은 PDF engine이 추가로 필요할 수 있습니다.

## 실제 장비 확장

- Test Case: `tests/pytest/test_cases/`
- Equipment Controller: `tests/pytest/test_equipments/`
- DUT Interface: `tests/pytest/test_interfaces/`
- 연결과 정리: `tests/pytest/conftest.py` fixture

CT에는 `@pytest.mark.ct(...)`와 `ct_result` fixture를 사용합니다. 테스트의 PASS/FAIL 여부와 관계없이 로그와 측정 자료가 실행 ID별로 생성됩니다.

## GitHub 자동화

일반 Unit Test와 mock CT는 GitHub-hosted runner에서 동작합니다. 실제 USB/JTAG 장비, vendor tool, 내부망 등 특수 실행 환경이 필요한 작업만 `Optional Special Environment Test` workflow와 `[self-hosted, hw-test]` runner를 사용합니다.
