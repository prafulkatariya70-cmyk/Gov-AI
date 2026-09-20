from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.job_source import JobSource


def get_sources_due_for_check(
    db: Session,
) -> list[JobSource]:
    """
    Return active job sources that are ready to be checked.

    All timestamps are treated as UTC.
    """

    now = datetime.utcnow()

    sources = (
        db.query(JobSource)
        .filter(JobSource.is_active.is_(True))
        .all()
    )

    due_sources = []

    for source in sources:

        if source.last_checked_at is None:
            due_sources.append(source)
            continue

        next_check_time = (
            source.last_checked_at
            + timedelta(
                minutes=source.check_interval_minutes
            )
        )

        if now >= next_check_time:
            due_sources.append(source)

    return due_sources