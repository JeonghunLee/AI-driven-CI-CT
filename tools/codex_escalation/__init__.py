from __future__ import annotations

from dataclasses import dataclass

from tools.deepseek import Analysis
from tools.result_normalizer import ResultRecord


@dataclass(frozen=True)
class EscalationDecision:
    required: bool
    reasons: tuple[str, ...]


def evaluate(result: ResultRecord, analysis: Analysis, repeated_failures: int = 0) -> EscalationDecision:
    reasons: list[str] = []
    if analysis.needs_escalation or analysis.confidence < 0.5:
        reasons.append("DeepSeek confidence is low or analysis is inconclusive")
    if result.status in {"FAIL", "ERROR"} and analysis.classification in {"unknown", "architecture", "multi-module"}:
        reasons.append("Root cause requires advanced analysis")
    if repeated_failures >= 2:
        reasons.append("Failure is repeated")
    return EscalationDecision(bool(reasons), tuple(reasons))


__all__ = ["EscalationDecision", "evaluate"]
