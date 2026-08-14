from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ERROR = re.compile(r"\b(error|exception|failed|fatal|traceback)\b", re.IGNORECASE)
WARNING = re.compile(r"\b(warn(?:ing)?|deprecated|retry)\b", re.IGNORECASE)
METRIC = re.compile(r"(?P<name>[A-Za-z][\w .-]+)\s*[=:]\s*(?P<value>-?\d+(?:\.\d+)?)")


@dataclass
class ParsedLog:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    important: list[str] = field(default_factory=list)


def parse_text(text: str, limit: int = 20) -> ParsedLog:
    parsed = ParsedLog()
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        match = METRIC.search(clean)
        numeric_error_metric = bool(match and match.group("name").strip().lower() == "error")
        has_error = bool(ERROR.search(clean)) and not numeric_error_metric
        has_warning = bool(WARNING.search(clean))
        if has_error and len(parsed.errors) < limit:
            parsed.errors.append(clean)
        elif has_warning and len(parsed.warnings) < limit:
            parsed.warnings.append(clean)
        if match:
            parsed.metrics[match.group("name").strip()] = float(match.group("value"))
        if (has_error or has_warning) and len(parsed.important) < limit:
            parsed.important.append(clean)
    return parsed


def parse_files(paths: list[str | Path]) -> ParsedLog:
    combined = ParsedLog()
    for path in paths:
        source = Path(path)
        if not source.exists():
            continue
        item = parse_text(source.read_text(encoding="utf-8", errors="replace"))
        combined.errors.extend(item.errors)
        combined.warnings.extend(item.warnings)
        combined.metrics.update(item.metrics)
        combined.important.extend(item.important)
    return combined


__all__ = ["ParsedLog", "parse_files", "parse_text"]
