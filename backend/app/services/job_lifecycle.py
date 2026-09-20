"""Server-side job freshness and lifecycle classification."""

from datetime import date, datetime, timezone

from sqlalchemy import func, or_

from app.models.job import Job

CLOSED_STATUSES = {"closed", "expired"}


def application_today() -> date:
    """The application-wide current date, evaluated in UTC."""
    return datetime.now(timezone.utc).date()


def lifecycle_status(job: Job, as_of: date | None = None) -> str:
    """Classify a job without changing source-provided persisted data."""
    today = as_of or application_today()
    status = (job.status or "").strip().lower()
    if status == "closed":
        return "CLOSED"
    if status == "expired" or (job.application_end is not None and job.application_end < today):
        return "EXPIRED"
    if job.application_start is not None and job.application_start > today:
        return "UPCOMING"
    if job.application_end is None:
        return "UNKNOWN"
    return "CURRENT"


def current_or_upcoming_filter(as_of: date):
    """SQL equivalent of the public-feed lifecycle rules."""
    return (
        ~func.lower(Job.status).in_(CLOSED_STATUSES),
        or_(Job.application_end.is_(None), Job.application_end >= as_of),
    )


def lifecycle_metadata(job: Job, as_of: date | None = None) -> dict[str, object]:
    today = as_of or application_today()
    state = lifecycle_status(job, today)
    days = (job.application_end - today).days if job.application_end is not None and state in {"CURRENT", "UPCOMING"} else None
    return {
        "lifecycle_status": state,
        "is_open": state == "CURRENT",
        "is_upcoming": state == "UPCOMING",
        "is_closing_soon": state == "CURRENT" and days is not None and days <= 7,
        "days_until_deadline": days,
    }
