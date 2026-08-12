from tools.codex_escalation.escalation import should_escalate_to_codex
from tools.github_reporter.issue_reporter import render_issue_comment
from tools.log_parser.parser import parse_log_summary
from tools.ollama.analyzer import ollama_first_analysis
from tools.result_normalizer.normalize import normalize_result


def test_result_pipeline_generates_issue_markdown_without_escalation():
    raw_result = {
        "test_id": "CT-UART-001",
        "execution_id": "20260812-001",
        "status": "FAIL",
        "category": "timing",
        "duration": 12.42,
        "interface": "UART",
        "equipment": "Saleae",
        "metrics": {"expected_baudrate": 921600, "measured_baudrate": 921502, "jitter": 0.028},
    }
    logs = "INFO start\nWARNING drift observed\nERROR UART jitter threshold exceeded"

    normalized = normalize_result(raw_result, commit="abcdef1", runner="hw-runner-01")
    parsed = parse_log_summary(logs)
    analysis = ollama_first_analysis(normalized, parsed)
    comment = render_issue_comment(normalized, parsed, analysis, artifact_uri="artifact://ct")

    assert normalized["status"] == "FAIL"
    assert parsed["errors"]
    assert "Ollama" in comment
    assert should_escalate_to_codex(analysis) is False


def test_result_pipeline_escalates_on_complex_failure():
    result = {
        "test_id": "CT-UART-001",
        "execution_id": "20260812-002",
        "status": "FAIL",
    }
    logs = "ERROR first\nERROR second"

    normalized = normalize_result(result, commit="abcdef1", runner="hw-runner-01")
    parsed = parse_log_summary(logs)
    analysis = ollama_first_analysis(normalized, parsed)

    assert analysis["classification"] == "Complex Failure"
    assert should_escalate_to_codex(analysis) is True
