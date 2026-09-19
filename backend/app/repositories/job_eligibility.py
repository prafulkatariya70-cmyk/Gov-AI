from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_eligibility import JobEligibility


class JobEligibilityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_job_id(self, job_id: UUID) -> JobEligibility | None:
        return self.db.execute(
            select(JobEligibility).where(JobEligibility.job_id == job_id)
        ).scalar_one_or_none()
