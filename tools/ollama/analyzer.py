def ollama_first_analysis(result: dict, parsed_logs: dict) -> dict:
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
