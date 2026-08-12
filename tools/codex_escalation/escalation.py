def should_escalate_to_codex(analysis: dict) -> bool:
    return bool(analysis.get("needs_codex", False))
