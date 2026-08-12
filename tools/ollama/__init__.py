from __future__ import annotations

import json
import os
from dataclasses import dataclass
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
    needs_escalation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class OllamaAnalyzer:
    def __init__(self, url: str | None = None, model: str | None = None, timeout: float = 8.0) -> None:
        self.url = (url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.timeout = timeout

    def analyze(self, result: ResultRecord, logs: ParsedLog) -> Analysis:
        prompt = self._prompt(result, logs)
        request = Request(
            f"{self.url}/api/generate",
            data=json.dumps({"model": self.model, "prompt": prompt, "stream": False, "format": "json"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                outer = json.load(response)
            parsed = json.loads(outer.get("response", "{}"))
            return Analysis(
                summary=str(parsed.get("summary", "Ollama returned no summary")),
                classification=str(parsed.get("classification", "unknown")),
                confidence=float(parsed.get("confidence", 0.5)),
                source="ollama",
                needs_escalation=bool(parsed.get("needs_escalation", False)),
            )
        except (URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
            return self._fallback(result, logs)

    @staticmethod
    def _fallback(result: ResultRecord, logs: ParsedLog) -> Analysis:
        if result.status == "PASS":
            summary = f"{result.test_id} passed in {result.duration:.3f}s."
            classification = "passed"
            confidence = 1.0
        else:
            detail = logs.errors[0] if logs.errors else "No explicit error was extracted from logs."
            summary = f"{result.test_id} ended with {result.status}. {detail}"
            classification = "test-failure" if logs.errors else "unknown"
            confidence = 0.7 if logs.errors else 0.3
        return Analysis(summary, classification, confidence, "deterministic-fallback", confidence < 0.5)

    @staticmethod
    def _prompt(result: ResultRecord, logs: ParsedLog) -> str:
        compact = {
            "result": result.to_dict(),
            "errors": logs.errors[:10],
            "warnings": logs.warnings[:10],
            "important": logs.important[:10],
        }
        return (
            "Analyze this test. Return only JSON with summary, classification, confidence (0..1), "
            "and needs_escalation. Do not invent evidence.\n" + json.dumps(compact, ensure_ascii=False)
        )


__all__ = ["Analysis", "OllamaAnalyzer"]

