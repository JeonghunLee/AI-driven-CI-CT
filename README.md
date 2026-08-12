# AI-driven CI/CT

GitHub Actions와 self-hosted runner에서 Unit Test 및 하드웨어 Continuous Test(CT)를 실행하고, 결과를 Ollama 우선으로 분석하는 자동화 프로젝트입니다. 복잡하거나 신뢰도가 낮은 실패만 Codex escalation 대상으로 분류합니다.

## 현재 구현 범위

- GitHub Test Request Issue Form과 `run-test` 라벨 기반 실행
- self-hosted runner용 Unit Test / Continuous Test workflow
- Python Unit Test 샘플
- 공통 `connect`, `disconnect`, `read`, `write`, `execute` 인터페이스
- Mock UART 및 Mock Saleae 장비
- UART baudrate/jitter CT 샘플
- 로그 디렉터리와 표준 `result.json` 생성
- 오류/경고/측정값 선행 파싱
- Ollama 분석과 연결 실패 시 deterministic fallback
- GitHub Issue 결과 코멘트
- MkDocs 상세 리포트와 테스트 이력
- Codex escalation 판단 인터페이스

실제 FPGA, Saleae, Digilent, USB, UART, JTAG, Network 드라이버는 각 분리된 디렉터리에 추가할 수 있으며, 기본 샘플은 장비 없이 실행됩니다.

## 로컬 실행

Python 3.10 이상을 권장합니다.

```powershell
python -m pip install -r requirements.txt
python -m pytest
python -m tools.pipeline --latest --docs
python -m mkdocs serve
```

Ollama가 실행 중이면 기본적으로 `http://127.0.0.1:11434`의 `qwen2.5-coder:7b` 모델을 사용합니다. 환경에 맞게 변경할 수 있습니다.

```powershell
$env:OLLAMA_URL = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "qwen2.5-coder:7b"
```

Ollama가 없거나 응답하지 않아도 파이프라인은 중단되지 않으며 규칙 기반 요약을 생성합니다.

## GitHub에서 실행

1. `Test request` Issue를 생성하고 항목을 선택합니다.
2. 준비된 Issue에 `run-test` 라벨을 추가합니다.
3. self-hosted runner에서 workflow가 실행됩니다.
4. 결과와 raw evidence는 Actions Artifact에 보존됩니다.
5. Issue에는 요약 코멘트가 추가되고 MkDocs용 문서가 생성됩니다.

수동 실행은 Actions의 `Continuous Test` workflow에서 `CT-UART-001`을 지정하면 됩니다.

## 결과 구조

```text
reports/
├── json/
│   ├── latest.json
│   └── latest-analysis.json
└── logs/<test-id>/<execution-id>/
    ├── result.json
    ├── analysis.json
    ├── codex-escalation.json
    ├── test.log
    ├── stdout.log
    ├── stderr.log
    ├── equipment.log
    └── interface.log
```

`reports/json/latest.json`이 후속 분석과 리포팅의 기준이며, 각 실행 원본은 실행 ID별 디렉터리에 유지됩니다.

## 실제 장비 확장

- DUT transport는 `tests/pytest/test_interfaces/` 아래에 구현합니다.
- 측정 장비 제어는 `tests/pytest/test_equipments/` 아래에 구현합니다.
- 테스트 시나리오는 `tests/pytest/test_cases/`에만 둡니다.
- 연결과 정리는 `conftest.py` fixture가 담당합니다.
- CT에는 `@pytest.mark.ct(...)` 메타데이터와 `ct_result` fixture를 사용하면 PASS/FAIL 여부와 무관하게 정규화 결과가 생성됩니다.

상세 설계 원칙과 전체 목표는 [Codex.md](Codex.md)를 참고하세요.
