from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
    jobs: list[JobSummary]
