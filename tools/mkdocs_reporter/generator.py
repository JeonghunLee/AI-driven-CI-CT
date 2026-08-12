from pathlib import Path


def render_mkdocs_report(result: dict, parsed_logs: dict, analysis: dict, issue_url: str) -> str:
    metrics = result.get("metrics", {})
    stats = result.get("statistics", {})
    important_logs = "\n".join(f"- {line}" for line in parsed_logs.get("important_logs", [])[:10]) or "- None"

    return f"""# {result.get('test_id', 'UNKNOWN')}

## Test Configuration
- Category: {result.get('category', 'unknown')}
- Interface: {result.get('interface', 'None')}
- Equipment: {result.get('equipment', 'None')}
- Status: {result.get('status', 'FAIL')}
- Execution ID: {result.get('execution_id', 'unknown')}
- Runner: {result.get('runner', 'unknown')}
- Commit: {result.get('commit', 'unknown')}

## Measurement
- expected_baudrate: {metrics.get('expected_baudrate', 'n/a')}
- measured_baudrate: {metrics.get('measured_baudrate', 'n/a')}
- error: {metrics.get('error', 'n/a')}
- jitter: {metrics.get('jitter', 'n/a')}

## Statistics
- mean: {stats.get('mean', 'n/a')}
- median: {stats.get('median', 'n/a')}
- min: {stats.get('min', 'n/a')}
- max: {stats.get('max', 'n/a')}
- stddev: {stats.get('stddev', 'n/a')}

## Important Log
{important_logs}

## AI Analysis
- Engine: {analysis.get('engine', 'ollama')}
- Summary: {analysis.get('summary', 'n/a')}
- Classification: {analysis.get('classification', 'unknown')}
- Confidence: {analysis.get('confidence', 'n/a')}

## Links
- GitHub Issue: {issue_url}
"""


def write_mkdocs_report(base_dir: str, category: str, test_id: str, markdown: str) -> str:
    path = Path(base_dir) / "docs" / "test" / "ct" / category.lower() / f"{test_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return str(path)
