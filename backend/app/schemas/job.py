from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
    reasons: list[str] = Field(default_factory=list)
    failed_requirements: list[str] = Field(default_factory=list)
    unknown_requirements: list[str] = Field(default_factory=list)
    passed_requirements: list[str] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    score: float | None = None
    confidence: str | None = None
