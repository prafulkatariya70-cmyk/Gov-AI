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
    evidence: list[dict[str, Any]] = field(default_factory=list)
    score: float | None = None


class EligibilityEngine:
    """Production boundary for the notification -> eligibility pipeline.

    The engine deliberately owns orchestration, not recruitment rules. The
    parser, normalizer and evaluator are injected so the already-tested rule
    engine can be connected without changing its behavior.
    """

    def __init__(self, parser: Parser, normalizer: Normalizer, evaluator: Evaluator) -> None:
        self._parser = parser
        self._normalizer = normalizer
        self._evaluator = evaluator

    def evaluate_notification(self, notification_text: str, candidate: Any) -> EligibilityResult:
        if not notification_text or not notification_text.strip():
            return EligibilityResult(
                status="NEEDS_REVIEW",
                reasons=["Notification text is empty or unavailable."],
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
                evidence=list(raw_result.get("evidence") or []),
                score=raw_result.get("score"),
            )

        status = getattr(raw_result, "status", "NEEDS_REVIEW")
        return EligibilityResult(
            status=str(status),
            reasons=list(getattr(raw_result, "reasons", []) or []),
            failed_requirements=list(getattr(raw_result, "failed_requirements", []) or []),
            evidence=list(getattr(raw_result, "evidence", []) or []),
            score=getattr(raw_result, "score", None),
        )
