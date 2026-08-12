def ollama_first_analysis(result: dict, parsed_logs: dict) -> dict:
    """Stub Ollama-first analyzer used for initial repository bootstrap.

    Escalation policy in this stub:
    - PASS => no escalation.
    - FAIL with one error => low-complexity failure (no escalation).
    - FAIL with two or more errors => complex failure (Codex escalation).
    """
    status = result.get("status", "FAIL")
    errors = parsed_logs.get("errors", [])

    confidence = 0.9
    classification = "PASS"
    summary = "Ollama summary: test passed."

    if status != "PASS":
        classification = "Complex Failure" if len(errors) > 1 else "Failure"
        summary = "Ollama summary: failure detected from result.json and parsed logs."
        confidence = 0.55 if classification == "Complex Failure" else 0.7

    return {
        "engine": "ollama",
        "summary": summary,
        "classification": classification,
        "confidence": confidence,
        "needs_codex": confidence < 0.65,
    }
