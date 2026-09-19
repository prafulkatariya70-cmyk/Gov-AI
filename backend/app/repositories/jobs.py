from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_jobs(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        category: str | None = None,
        job_type: str | None = None,
        state: str | None = None,
        qualification: str | None = None,
        status: str | None = None,
    ) -> tuple[int, list[Job]]:
        filters = []
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Job.title.ilike(term),
                    Job.board.ilike(term),
                    Job.board_code.ilike(term),
                    Job.post_name.ilike(term),
                )
            )
        if category and category not in {"All", "All Categories"}:
            filters.append(Job.category.ilike(f"%{category}%"))
        if job_type and job_type not in {"All", "All Types"}:
            filters.append(Job.job_type == job_type)
        if state and state not in {"All", "All India", "All States"}:
            filters.append(or_(Job.state.ilike(f"%{state}%"), Job.state == "All India"))
        if qualification and qualification not in {"All", "All Qualifications"}:
            filters.append(Job.qualification_required.ilike(f"%{qualification}%"))
        if status and status not in {"All", "All Statuses"}:
            filters.append(Job.status == status)

        base = select(Job)
        count_query = select(func.count()).select_from(Job)
        if filters:
            base = base.where(*filters)
            count_query = count_query.where(*filters)

        total = self.db.execute(count_query).scalar_one()
        offset = (page - 1) * page_size
        jobs = self.db.execute(
            base.order_by(Job.created_at.desc(), Job.id).offset(offset).limit(page_size)
        ).scalars().all()
        return total, jobs

    def get_by_id_or_slug(self, identifier: str) -> Job | None:
        stmt = select(Job).where(Job.slug == identifier)
        try:
            from uuid import UUID
            job_id = UUID(identifier)
        except ValueError:
            job_id = None
        if job_id:
            stmt = select(Job).where(or_(Job.id == job_id, Job.slug == identifier))
        return self.db.execute(stmt).scalar_one_or_none()
