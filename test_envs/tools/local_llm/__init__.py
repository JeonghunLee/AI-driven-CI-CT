from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from test_envs.tools.log_parser import ParsedLog
from test_envs.tools.result_normalizer import ResultRecord
from test_envs.tools.configuration import load_config

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def _resolve_model_from_config(config: dict[str, Any]) -> str | None:
    ollama = config.get("ollama")
    if isinstance(ollama, dict):
        selected_model = ollama.get("selected_model")
        if isinstance(selected_model, str) and selected_model.strip():
            return selected_model.strip()
    models = config.get("models")
    preset = config.get("selected")
    if isinstance(models, dict) and isinstance(preset, str):
        model = models.get(preset)
        if isinstance(model, str) and model.strip():
            return model.strip()
        if isinstance(model, dict):
            name = model.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
    model = config.get("model")
    if isinstance(model, str) and model.strip():
        return model.strip()
    return None


def selected_model(explicit: str | None = None) -> str:
    config = load_config()
    model = explicit or os.getenv("OLLAMA_MODEL") or _resolve_model_from_config(config)
    if not model:
        raise RuntimeError("Ollama model is not configured in test_envs/config/config.json")
    return model


def selected_url(explicit: str | None = None) -> str:
    config = load_config()
    ollama = config.get("ollama")
    config_url = ollama.get("url") if isinstance(ollama, dict) else config.get("url")
    return (explicit or os.getenv("OLLAMA_URL") or (config_url if isinstance(config_url, str) else DEFAULT_OLLAMA_URL)).rstrip("/")


@dataclass(frozen=True)
class InstalledModel:
    name: str
    size: int = 0
    modified_at: str = ""
    digest: str = ""

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "InstalledModel":
        return cls(
            name=str(value.get("name") or value.get("model") or ""),
            size=int(value.get("size", 0)),
            modified_at=str(value.get("modified_at", "")),
            digest=str(value.get("digest", "")),
        )


def installed_models(url: str | None = None, timeout: float = 3.0) -> list[InstalledModel]:
    with urlopen(f"{selected_url(url)}/api/tags", timeout=timeout) as response:
        payload = json.load(response)
    values = payload.get("models", [])
    if not isinstance(values, list):
        raise ValueError("Ollama /api/tags response does not contain a model list")
    return [InstalledModel.from_dict(value) for value in values if isinstance(value, dict)]


def runtime_status(url: str | None = None) -> dict[str, Any]:
    configured = selected_model()
    endpoint = selected_url(url)
    try:
        models = installed_models(endpoint)
        names = [model.name for model in models]
        return {
            "endpoint": endpoint,
            "configured_model": configured,
            "configured_model_installed": configured in names,
            "installed_models": [asdict(model) for model in models],
            "available": True,
        }
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        return {
            "endpoint": endpoint,
            "configured_model": configured,
            "configured_model_installed": False,
            "installed_models": [],
            "available": False,
            "error": str(error),
        }


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


class LocalLLMAnalyzer:
    def __init__(self, url: str | None = None, model: str | None = None, timeout: float = 20.0) -> None:
        self.url = selected_url(url)
        self.model = selected_model(model)
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
            required = {"summary", "classification", "confidence"}
            if not isinstance(value, dict) or not required.issubset(value):
                raise ValueError("Local LLM response is missing required analysis fields")
            warnings = value.get("warnings", [])
            if not isinstance(warnings, list):
                raise ValueError("Local LLM warnings must be a list")
            return Analysis(
                summary=str(value["summary"]),
                classification=str(value["classification"]),
                confidence=float(value["confidence"]),
                source=f"ollama/{self.model}",
                warnings=warnings,
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


__all__ = [
    "Analysis",
    "DEFAULT_OLLAMA_URL",
    "InstalledModel",
    "LocalLLMAnalyzer",
    "installed_models",
    "runtime_status",
    "selected_model",
    "selected_url",
]
