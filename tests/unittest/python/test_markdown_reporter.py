from tools.deepseek import Analysis
from tools.mkdocs_reporter import MarkdownReporter
from tools.result_normalizer import ResultRecord, ResultStore


def test_markdown_first_report_contains_required_sections() -> None:
    root = "reports/test-artifacts/markdown-reporter"
    result = ResultRecord(
        "CT-MD-001", "PASS", "timing", 0.2,
        description="UART timing", environment="test", equipment="Saleae", interface="UART",
        metrics={"jitter": 0.001},
    )
    ResultStore(root).save(result)
    path = MarkdownReporter(root).generate(result, Analysis("Stable", "passed", 1.0, "test"))
    text = path.read_text(encoding="utf-8")
    assert "## DeepSeek analysis" in text
    assert "## Warnings" in text
    assert "## Test history" in text
