from tools.mkdocs_reporter.generator import render_mkdocs_report


def test_render_mkdocs_report_contains_sections():
    result = {
        "test_id": "CT-UART-001",
        "status": "PASS",
        "category": "timing",
        "interface": "UART",
        "equipment": "Saleae",
        "execution_id": "20260812-001",
        "runner": "hw-runner-01",
        "commit": "abcdef1",
        "metrics": {"expected_baudrate": 921600, "measured_baudrate": 921502},
    }
    parsed_logs = {"important_logs": ["WARNING drift"]}
    analysis = {"engine": "ollama", "summary": "ok", "classification": "PASS", "confidence": 0.9}

    report = render_mkdocs_report(result, parsed_logs, analysis, "https://github.com/example/issues/1")

    assert "# CT-UART-001" in report
    assert "## AI Analysis" in report
    assert "GitHub Issue" in report
