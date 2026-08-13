from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from tools.log_parser import ParsedLog
from tools.result_normalizer import ResultRecord


@dataclass
class Analysis:
    summary: str
    classification: str
    confidence: float
    source: str
    warnings: list[dict[str, str]] = field(default_factory=list)
    failure_analysis: str = ""
    source_review: str = "Not requested"
    needs_escalation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DeepSeekAnalyzer:
    """Use a DeepSeek model through the local Ollama runtime."""

    def __init__(self, url: str | None = None, model: str | None = None, timeout: float = 20.0) -> None:
        self.url = (url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-r1:7b")
        self.timeout = timeout

    def analyze(self, result: ResultRecord, logs: ParsedLog, source_diff: str = "") -> Analysis:
        request = Request(
            f"{self.url}/api/generate",
            data=json.dumps(
                {"model": self.model, "prompt": self._prompt(result, logs, source_diff), "stream": False, "format": "json"}
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                outer = json.load(response)
            value = json.loads(outer.get("response", "{}"))
            return Analysis(
                summary=str(value.get("summary", "DeepSeek returned no summary")),
                classification=str(value.get("classification", "unknown")),
                confidence=float(value.get("confidence", 0.5)),
                source=f"ollama/{self.model}",
                warnings=list(value.get("warnings", [])),
                failure_analysis=str(value.get("failure_analysis", "")),
                source_review=str(value.get("source_review", "Not requested")),
                needs_escalation=bool(value.get("needs_escalation", False)),
            )
        except (URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
            return self._fallback(result, logs)

    @staticmethod
    def _fallback(result: ResultRecord, logs: ParsedLog) -> Analysis:
        warnings = [{"severity": "Important", "message": line} for line in logs.warnings]
        if result.status == "PASS":
            return Analysis(
                summary=f"{result.test_id} passed in {result.duration:.3f}s.",
                classification="passed",
                confidence=1.0,
                source="deterministic-fallback",
                warnings=warnings,
            )
        detail = logs.errors[0] if logs.errors else "No explicit error was extracted from logs."
        confidence = 0.7 if logs.errors else 0.3
        return Analysis(
            summary=f"{result.test_id} ended with {result.status}.",
            classification="test-failure" if logs.errors else "unknown",
            confidence=confidence,
            source="deterministic-fallback",
            warnings=warnings,
            failure_analysis=detail,
            needs_escalation=confidence < 0.5,
        )

    @staticmethod
    def _prompt(result: ResultRecord, logs: ParsedLog, source_diff: str) -> str:
        evidence = {
            "test_result": result.to_dict(),
            "errors": logs.errors[:20],
            "warnings": logs.warnings[:20],
            "important_logs": logs.important[:20],
            "source_diff": source_diff[:12000],
        }
        return (
            "Analyze test, log, warning, and optional source diff evidence. Return only JSON containing "
            "summary, classification, confidence, warnings (severity/message), failure_analysis, "
            "source_review, needs_escalation. Warning severity must be Critical, Important, or Low. "
            "Do not invent evidence.\n" + json.dumps(evidence, ensure_ascii=False)
        )


__all__ = ["Analysis", "DeepSeekAnalyzer"]
