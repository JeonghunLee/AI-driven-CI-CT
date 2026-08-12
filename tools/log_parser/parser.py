def parse_log_summary(log_text: str) -> dict:
    errors = []
    warnings = []
    important = []

    for line in log_text.splitlines():
        upper = line.upper()
        if "ERROR" in upper:
            errors.append(line)
            important.append(line)
        elif "WARN" in upper:
            warnings.append(line)
            important.append(line)

    return {
        "errors": errors,
        "warnings": warnings,
        "important_logs": important[:20],
    }
