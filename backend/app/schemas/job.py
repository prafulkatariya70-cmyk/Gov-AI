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
