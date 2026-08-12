def render_issue_comment(result: dict, parsed_logs: dict, analysis: dict, artifact_uri: str) -> str:
    metrics = result.get("metrics", {})
    statistics = result.get("statistics", {})

    return f"""## Test Result

Result: {result.get('status', 'FAIL')}

Test
- Type: {'CT' if 'CT' in result.get('test_id', '') else 'Unit'}
- Category: {result.get('category', 'unknown')}
- Interface: {result.get('interface', 'None')}
- Equipment: {result.get('equipment', 'None')}

Measurement
- Expected Baudrate: {metrics.get('expected_baudrate', 'n/a')}
- Measured Baudrate: {metrics.get('measured_baudrate', 'n/a')}
- Error: {metrics.get('error', 'n/a')}
- Jitter: {metrics.get('jitter', 'n/a')}

Statistics
- Mean: {statistics.get('mean', 'n/a')}
- Median: {statistics.get('median', 'n/a')}
- Min: {statistics.get('min', 'n/a')}
- Max: {statistics.get('max', 'n/a')}
- Std Dev: {statistics.get('stddev', 'n/a')}

Failure
- {parsed_logs.get('errors', ['None'])[0] if parsed_logs.get('errors') else 'None'}

AI Analysis
- Ollama generated summary: {analysis.get('summary', 'n/a')}

Logs
- Artifact available: {artifact_uri}

Commit: {result.get('commit', 'unknown')}
Runner: {result.get('runner', 'unknown')}
Execution ID: {result.get('execution_id', 'unknown')}
"""
