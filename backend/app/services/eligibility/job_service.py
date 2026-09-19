from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from app.repositories.job_eligibility import JobEligibilityRepository
from app.repositories.user_profiles import UserProfileRepository
from app.services.documents.parsing.rules.models import (
    EligibilityRule,
    EligibilityRuleGroup,
    NormalizedEligibility,
)
from app.services.eligibility.evaluator import EligibilityEvaluator
from app.services.eligibility.models import CandidateProfile
from app.services.eligibility.service import EligibilityResult


class PersistedEligibilityService:
    """Evaluate a user against eligibility rules already persisted in PostgreSQL.

    Ingestion owns parsing/normalization. Request-time evaluation only reconstructs
    the persisted rule tree and delegates the decision to the existing evaluator.
    """

    def __init__(self, db) -> None:
        self.job_eligibility = JobEligibilityRepository(db)
        self.user_profiles = UserProfileRepository(db)
        self.evaluator = EligibilityEvaluator()

    def evaluate(self, job_id: UUID, user_id: UUID) -> EligibilityResult:
        eligibility = self.job_eligibility.get_by_job_id(job_id)
        if eligibility is None or not eligibility.normalized_rules:
            return EligibilityResult(
                status="NEEDS_REVIEW",
                reasons=["Eligibility rules are not available for this job."],
                confidence="low",
            )

        profile = self.user_profiles.get_by_user_id(user_id)
        if profile is None:
            return EligibilityResult(
                status="NEEDS_REVIEW",
                reasons=["Candidate profile is incomplete or unavailable."],
                confidence="low",
            )

        candidate = self._to_candidate(profile)
        rules = self._from_dict(eligibility.normalized_rules)
        return self._coerce_result(self.evaluator.evaluate(candidate, rules))

    @staticmethod
    def _to_candidate(profile) -> CandidateProfile:
        qualification_parts = [
            profile.qualification,
            profile.degree_name,
            profile.stream,
            profile.additional_certs,
        ]
        qualification_text = " ".join(
            str(value).strip()
            for value in qualification_parts
            if value and str(value).strip()
        ) or None

        return CandidateProfile(
            age=PersistedEligibilityService._calculate_age(profile.dob),
            government_employee=profile.government_employee,
            analogous_post=profile.analogous_post,
            regular_service_years=profile.regular_service_years,
            current_pay_level=profile.current_pay_level,
            parent_cadre=profile.parent_cadre,
            qualifying_examination=profile.qualifying_examination,
            required_training=profile.required_training,
            relevant_experience_years=profile.relevant_experience_years,
            experience_areas=list(profile.experience_areas or []),
            qualification_text=qualification_text,
        )

    @staticmethod
    def _calculate_age(dob: date | None, today: date | None = None) -> int | None:
        if dob is None:
            return None
        current = today or date.today()
        age = current.year - dob.year
        if (current.month, current.day) < (dob.month, dob.day):
            age -= 1
        return age

    @classmethod
    def _from_dict(cls, payload: dict[str, Any]) -> NormalizedEligibility:
        return NormalizedEligibility(
            age_rules=cls._rules(payload.get("age_rules")),
            service_rules=cls._rules(payload.get("service_rules")),
            qualification_rules=cls._rules(payload.get("qualification_rules")),
            experience_rules=cls._rules(payload.get("experience_rules")),
            department_rules=cls._rules(payload.get("department_rules")),
            special_rules=cls._rules(payload.get("special_rules")),
            pay_rules=cls._rules(payload.get("pay_rules")),
        )

    @classmethod
    def _rules(cls, values: Any) -> list:
        if not isinstance(values, list):
            return []
        return [cls._node(value) for value in values]

    @classmethod
    def _node(cls, value: Any):
        if not isinstance(value, dict):
            raise ValueError("Invalid persisted eligibility rule node")

        if "operator" in value:
            operator = value.get("operator")
            if operator not in {"AND", "OR"}:
                raise ValueError("Invalid persisted eligibility rule operator")
            return EligibilityRuleGroup(
                operator=operator,
                rules=[cls._node(item) for item in value.get("rules", [])],
            )

        rule_type = value.get("rule_type")
        if not rule_type:
            raise ValueError("Persisted eligibility rule is missing rule_type")

        return EligibilityRule(
            rule_type=str(rule_type),
            value=value.get("value"),
            confidence=str(value.get("confidence", "low")),
            evidence=value.get("evidence"),
            metadata=value.get("metadata") or {},
        )

    @staticmethod
    def _coerce_result(raw_result) -> EligibilityResult:
        return EligibilityResult(
            status=str(raw_result.status),
            reasons=list(raw_result.reasons or []),
            failed_requirements=[str(item.reason or item.rule_type) for item in raw_result.failed],
            unknown_requirements=[str(item.reason or item.rule_type) for item in raw_result.unknown],
            passed_requirements=[str(item.rule_type) for item in raw_result.passed],
            evidence=[
                {
                    "rule_type": item.rule_type,
                    "status": item.status,
                    "required": item.required,
                    "actual": item.actual,
                    "reason": item.reason,
                    "evidence": item.evidence,
                    "confidence": item.confidence,
                }
                for item in raw_result.requirements
            ],
            confidence=raw_result.confidence,
        )
