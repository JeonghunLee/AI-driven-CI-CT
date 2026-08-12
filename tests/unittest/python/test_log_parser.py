from tools.log_parser import parse_text


def test_numeric_error_metric_is_not_failure_log() -> None:
    parsed = parse_text("error=0.0001\nERROR connection lost")
    assert parsed.metrics["error"] == 0.0001
    assert parsed.errors == ["ERROR connection lost"]
    assert parsed.important == ["ERROR connection lost"]
