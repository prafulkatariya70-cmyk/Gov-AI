from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    board: str
    board_code: str
    job_type: str
    state: str
    category: str
    post_name: str
    total_vacancies: int
    qualification_required: str | None = None
    qualification_details: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    notification_date: date | None = None
    start_date: date | None = None
    last_date: date | None = None
    exam_date: str | None = None
    official_apply_url: str | None = None
    official_notification_pdf_url: str | None = None
    official_website_url: str | None = None
    salary_scale: str | None = None
    status: str
    is_featured: bool
    is_new_today: bool
    is_closing_soon: bool
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    jobs: list[JobSummary] = Field(default_factory=list)


class JobEligibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
