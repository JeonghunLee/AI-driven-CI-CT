from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from test_envs.tools.log_parser import ParsedLog
from test_envs.tools.result_normalizer import ResultRecord
from test_envs.tools.configuration import configured_now, load_config

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_LOG_ROOT = Path(__file__).resolve().parents[2] / "reports" / "local_llm"

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "classification": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "warnings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["Critical", "Important", "Low"]},
                    "message": {"type": "string"},
                },
                "required": ["severity", "message"],
            },
        },
        "failure_analysis": {"type": "string"},
        "source_review": {"type": "string"},
        "needs_escalation": {"type": "boolean"},
    },
    "required": [
        "summary",
        "classification",
        "confidence",
        "warnings",
        "failure_analysis",
        "source_review",
        "needs_escalation",
    ],
}


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
        raise RuntimeError("Ollama model is not configured in test_envs/configs/config.json")
    return model


def selected_url(explicit: str | None = None) -> str:
    config = load_config()
    ollama = config.get("ollama")
    config_url = ollama.get("url") if isinstance(ollama, dict) else config.get("url")
    return (explicit or os.getenv("OLLAMA_URL") or (config_url if isinstance(config_url, str) else DEFAULT_OLLAMA_URL)).rstrip("/")


def _configured_analysis() -> tuple[str, float, int]:
    ollama = load_config().get("ollama", {})
    if not isinstance(ollama, dict):
        raise RuntimeError("Invalid project configuration: ollama must be an object")
    prompt = ollama.get("prompt", "result.json analysis")
    timeout = ollama.get("max_timeout_s", 20)
    retry = ollama.get("max_retry", 3)
    try:
        timeout_value = float(timeout)
        retry_value = int(retry)
    except (TypeError, ValueError) as error:
        raise RuntimeError("Invalid Local LLM timeout or retry configuration") from error
    if not isinstance(prompt, str) or not prompt.strip():
        raise RuntimeError("Invalid Local LLM prompt configuration")
    if timeout_value <= 0 or retry_value < 0:
        raise RuntimeError("Local LLM timeout must be positive and retry cannot be negative")
    return prompt.strip(), timeout_value, retry_value


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
    prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LocalLLMAnalyzer:
    def __init__(
        self,
        url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_retry: int | None = None,
        prompt: str | None = None,
        log_root: str | Path | None = None,
    ) -> None:
        configured_prompt, configured_timeout, configured_retry = _configured_analysis()
        self.url = selected_url(url)
        self.model = selected_model(model)
        self.timeout = configured_timeout if timeout is None else timeout
        self.max_retry = configured_retry if max_retry is None else max_retry
        self.prompt = configured_prompt if prompt is None else prompt
        self.log_root = Path(log_root) if log_root else DEFAULT_LOG_ROOT

    def analyze(self, result: ResultRecord, logs: ParsedLog, source_diff: str = "") -> Analysis:
        entries = [
            f"timestamp={configured_now().isoformat()}",
            f"execution_id={result.execution_id}",
            f"test_id={result.test_id}",
            f"model={self.model}",
            f"endpoint={self.url}",
            f"timeout_s={self.timeout}",
            f"max_retry={self.max_retry}",
        ]
        for attempt in range(1, self.max_retry + 2):
            raw_response = ""
            request = Request(
                f"{self.url}/api/generate",
                data=json.dumps(
                    {
                        "model": self.model,
                        "prompt": self._prompt(result, logs, source_diff),
                        "stream": False,
                        "format": ANALYSIS_SCHEMA,
                    },
                    ensure_ascii=False,
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    outer = json.load(response)
                raw_response = str(outer.get("response", "{}"))
                value = json.loads(raw_response)
                required = set(ANALYSIS_SCHEMA["required"])
                if not isinstance(value, dict) or not required.issubset(value):
                    raise ValueError("Local LLM response is missing required analysis fields")
                warnings = value["warnings"]
                if not isinstance(warnings, list) or not all(isinstance(item, dict) for item in warnings):
                    raise ValueError("Local LLM warnings must be a list of objects")
                confidence = float(value["confidence"])
                if not 0.0 <= confidence <= 1.0:
                    raise ValueError("Local LLM confidence must be between 0.0 and 1.0")
                entries.extend([f"\n[ATTEMPT {attempt}]", "status=success", f"response={raw_response}"])
                self._write_log(result.execution_id, entries)
                return Analysis(
                    summary=str(value["summary"]),
                    classification=str(value["classification"]),
                    confidence=confidence,
                    source=f"ollama/{self.model}",
                    warnings=warnings,
                    failure_analysis=str(value["failure_analysis"]),
                    source_review=str(value["source_review"]),
                    needs_escalation=bool(value["needs_escalation"]),
                    prompt=self.prompt,
                )
            except (URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as error:
                entries.extend(
                    [
                        f"\n[ATTEMPT {attempt}]",
                        "status=error",
                        f"error={type(error).__name__}: {error}",
                        f"response={raw_response}",
                    ]
                )
                self._write_log(result.execution_id, entries)
        fallback = self._fallback(result, logs)
        fallback.prompt = self.prompt
        entries.extend(["\n[FALLBACK]", f"source={fallback.source}"])
        self._write_log(result.execution_id, entries)
        return fallback

    def _write_log(self, execution_id: str, entries: list[str]) -> Path:
        self.log_root.mkdir(parents=True, exist_ok=True)
        path = self.log_root / f"{execution_id}_local_llm.log"
        path.write_text("\n".join(entries) + "\n", encoding="utf-8")
        return path

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

    def _prompt(self, result: ResultRecord, logs: ParsedLog, source_diff: str) -> str:
        evidence = {
            "test_result": result.to_dict(),
            "errors": logs.errors[:20],
            "warnings": logs.warnings[:20],
            "important_logs": logs.important[:20],
            "source_diff": source_diff[:12000],
        }
        return (
            f"{self.prompt}. "
            "Analyze test, log, warning, and optional source diff evidence. Return only JSON containing "
            "summary, classification, confidence (0.0 to 1.0), warnings (severity/message), failure_analysis, "
            "source_review, needs_escalation. Warning severity must be Critical, Important, or Low. "
            "Do not invent evidence.\n" + json.dumps(evidence, ensure_ascii=False)
        )


__all__ = [
    "Analysis",
    "ANALYSIS_SCHEMA",
    "DEFAULT_OLLAMA_URL",
    "DEFAULT_LOG_ROOT",
    "InstalledModel",
    "LocalLLMAnalyzer",
    "installed_models",
    "runtime_status",
    "selected_model",
    "selected_url",
]
