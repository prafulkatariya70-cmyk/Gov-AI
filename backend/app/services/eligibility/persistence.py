from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_eligibility import JobEligibility
from app.services.documents.parsing.notification_parser import ParsedNotification
from app.services.documents.parsing.rules.models import (
    EligibilityRule,
    EligibilityRuleGroup,
    NormalizedEligibility,
)
from app.services.documents.parsing.rules.normalizer import EligibilityNormalizer


def _serialize_rule(value: Any) -> Any:
    """Convert eligibility dataclasses into JSON-safe primitives."""
    if isinstance(value, (EligibilityRule, EligibilityRuleGroup, NormalizedEligibility)):
        return {key: _serialize_rule(item) for key, item in asdict(value).items()}
    if is_dataclass(value):
        return {key: _serialize_rule(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _serialize_rule(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_rule(item) for item in value]
    return value


class EligibilityPersistence:
    """Persist parsed and normalized eligibility requirements for a job."""

    def __init__(self, db: Session, normalizer: EligibilityNormalizer | None = None) -> None:
        self._db = db
        self._normalizer = normalizer or EligibilityNormalizer()

    def persist(
        self,
        job: Job,
        parsed: ParsedNotification,
        normalized: NormalizedEligibility | None = None,
    ) -> JobEligibility:
        if job.id is None:
            raise ValueError("Job must have a database id before eligibility can be persisted.")

        normalized = normalized or self._normalizer.normalize(parsed)

        eligibility = self._db.query(JobEligibility).filter(
            JobEligibility.job_id == job.id
        ).one_or_none()

        if eligibility is None:
            eligibility = JobEligibility(job_id=job.id)
            self._db.add(eligibility)

        eligibility.normalized_rules = _serialize_rule(normalized)
        eligibility.qualification_text = self._field_value(parsed, "qualification_text")
        eligibility.experience_requirement = self._field_value(parsed, "experience_requirement")
        eligibility.service_requirement = self._field_value(parsed, "service_requirement")
        eligibility.department_requirement = self._field_value(parsed, "department_requirement")
        eligibility.special_requirements = self._field_value(parsed, "special_requirements")

        self._db.flush()
        return eligibility

    @staticmethod
    def _field_value(parsed: ParsedNotification, field_name: str) -> str | None:
        field = getattr(parsed, field_name)
        value = field.value
        if value is None:
            return None
        return str(value)
