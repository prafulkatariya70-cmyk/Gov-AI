from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobEligibilityResponse(BaseModel):
    id: UUID
    job_id: UUID
    normalized_rules: dict | None = None
    qualification_text: str | None = None
    experience_requirement: str | None = None
    service_requirement: str | None = None
    department_requirement: str | None = None
    special_requirements: str | None = None
    created_at: datetime
    updated_at: datetime


class EligibilityDecisionResponse(BaseModel):
    status: str
    reasons: list[str] = []
    failed_requirements: list[str] = []
    unknown_requirements: list[str] = []
    passed_requirements: list[str] = []
    evidence: list[dict] = []
    score: float | None = None
    confidence: str | None = None
