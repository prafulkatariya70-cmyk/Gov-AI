from dataclasses import dataclass

from app.services.eligibility.service import EligibilityEngine, EligibilityResult


@dataclass
class Parsed:
    value: str


@dataclass
class Normalized:
    value: str


class FakeParser:
    def parse(self, text: str):
        return Parsed(text.strip())


class FakeNormalizer:
    def normalize(self, parsed):
        return Normalized(parsed.value.upper())


class FakeEvaluator:
    def evaluate(self, candidate, normalized):
        assert candidate == {"id": "candidate-1"}
        assert normalized.value == "NOTIFICATION"
        return {
            "status": "ELIGIBLE",
            "reasons": ["Qualification requirement satisfied."],
            "failed_requirements": [],
            "evidence": [{"field": "qualification", "text": "B.E."}],
            "score": 100,
        }


def test_engine_orchestrates_parser_normalizer_evaluator():
    engine = EligibilityEngine(FakeParser(), FakeNormalizer(), FakeEvaluator())

    result = engine.evaluate_notification(" notification ", {"id": "candidate-1"})

    assert result == EligibilityResult(
        status="ELIGIBLE",
        reasons=["Qualification requirement satisfied."],
        failed_requirements=[],
        evidence=[{"field": "qualification", "text": "B.E."}],
        score=100,
    )


def test_empty_notification_is_needs_review_without_running_rules():
    class ExplodingParser:
        def parse(self, text):
            raise AssertionError("parser must not run for empty input")

    engine = EligibilityEngine(ExplodingParser(), FakeNormalizer(), FakeEvaluator())
    result = engine.evaluate_notification("   ", {"id": "candidate-1"})

    assert result.status == "NEEDS_REVIEW"
    assert result.reasons == ["Notification text is empty or unavailable."]
