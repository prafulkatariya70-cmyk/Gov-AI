from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application_tracker import ApplicationTracker
from app.models.job import Job


class ApplicationTrackerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user_id: UUID) -> list[tuple[ApplicationTracker, Job]]:
        return list(self.db.execute(
            select(ApplicationTracker, Job)
            .join(Job, Job.id == ApplicationTracker.job_id)
            .where(ApplicationTracker.user_id == user_id)
            .order_by(ApplicationTracker.updated_at.desc())
        ).all())

    def get(self, user_id: UUID, job_id: UUID) -> ApplicationTracker | None:
        return self.db.execute(
            select(ApplicationTracker).where(
                ApplicationTracker.user_id == user_id,
                ApplicationTracker.job_id == job_id,
            )
        ).scalar_one_or_none()

    def upsert(self, user_id: UUID, job_id: UUID, values: dict) -> ApplicationTracker:
        item = self.get(user_id, job_id)
        if item is None:
            item = ApplicationTracker(user_id=user_id, job_id=job_id, **values)
            self.db.add(item)
        else:
            for field, value in values.items():
                if value is not None:
                    setattr(item, field, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove(self, user_id: UUID, job_id: UUID) -> bool:
        item = self.get(user_id, job_id)
        if item is None:
            return False
        self.db.delete(item)
        self.db.commit()
        return True
