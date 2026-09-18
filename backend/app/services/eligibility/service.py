from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class Parser(Protocol):
    def parse(self, text: str) -> Any: ...


class Normalizer(Protocol):
    def normalize(self, parsed: Any) -> Any: ...


class Evaluator(Protocol):
    def evaluate(self, candidate: Any, normalized: Any) -> Any: ...


@dataclass(frozen=True)
class EligibilityResult:
    status: str
    reasons: list[str] = field(default_factory=list)
    failed_requirements: list[str] = field(default_factory=list)
    unknown_requirements: list[str] = field(default_factory=list)
    passed_requirements: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    score: float | None = None
    confidence: str | None = None


class EligibilityEngine:
    """Production boundary for the notification -> eligibility pipeline."""

    def __init__(self, parser: Parser, normalizer: Normalizer, evaluator: Evaluator) -> None:
        self._parser = parser
        self._normalizer = normalizer
        self._evaluator = evaluator

    def evaluate_notification(self, notification_text: str, candidate: Any) -> EligibilityResult:
        if not notification_text or not notification_text.strip():
            return EligibilityResult(
                status="NEEDS_REVIEW",
                reasons=["Notification text is empty or unavailable."],
                confidence="low",
            )

        parsed = self._parser.parse(notification_text)
        normalized = self._normalizer.normalize(parsed)
        raw_result = self._evaluator.evaluate(candidate, normalized)
        return self._coerce_result(raw_result)

    @staticmethod
    def _coerce_result(raw_result: Any) -> EligibilityResult:
        if isinstance(raw_result, EligibilityResult):
            return raw_result

        if isinstance(raw_result, dict):
            return EligibilityResult(
                status=str(raw_result.get("status", "NEEDS_REVIEW")),
                reasons=list(raw_result.get("reasons") or []),
                failed_requirements=list(raw_result.get("failed_requirements") or []),
                unknown_requirements=list(raw_result.get("unknown_requirements") or []),
                passed_requirements=list(raw_result.get("passed_requirements") or []),
                evidence=list(raw_result.get("evidence") or []),
                score=raw_result.get("score"),
                confidence=raw_result.get("confidence"),
            )

        failed = list(getattr(raw_result, "failed", []) or [])
        unknown = list(getattr(raw_result, "unknown", []) or [])
        passed = list(getattr(raw_result, "passed", []) or [])
        requirements = list(getattr(raw_result, "requirements", []) or [])

        def reason(item: Any) -> str:
            return str(getattr(item, "reason", item))

        def evidence(item: Any) -> dict[str, Any]:
            return {
                "rule_type": getattr(item, "rule_type", None),
                "status": getattr(item, "status", None),
                "evidence": getattr(item, "evidence", None),
                "confidence": getattr(item, "confidence", None),
            }

        return EligibilityResult(
            status=str(getattr(raw_result, "status", "NEEDS_REVIEW")),
            reasons=list(getattr(raw_result, "reasons", []) or []),
            failed_requirements=[reason(item) for item in failed],
            unknown_requirements=[reason(item) for item in unknown],
            passed_requirements=[str(getattr(item, "rule_type", item)) for item in passed],
            evidence=[evidence(item) for item in requirements],
            score=getattr(raw_result, "score", None),
            confidence=getattr(raw_result, "confidence", None),
        )
