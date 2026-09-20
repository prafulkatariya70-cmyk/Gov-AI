import hashlib

from sqlalchemy.orm import Session

from app.models.job import Job
from app.services.ingestion.models import DiscoveredJob


def normalize_text(value: str | None) -> str:
    """
    Normalize text for reliable comparisons.
    """

    if not value:
        return ""

    return " ".join(value.lower().split())


def build_job_fingerprint(job: DiscoveredJob) -> str:
    """
    Build a deterministic fingerprint for a discovered job.

    External IDs are preferred because they are normally
    provided by the source itself.

    If no external ID exists, use a combination of:
    organization + title + application end date.
    """

    if job.external_id:
        raw_value = (
            f"{normalize_text(job.source_name)}|"
            f"{normalize_text(job.external_id)}"
        )
    else:
        raw_value = (
            f"{normalize_text(job.organization_name)}|"
            f"{normalize_text(job.title)}|"
            f"{job.application_end or ''}"
        )

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def find_existing_job(
    db: Session,
    discovered_job: DiscoveredJob,
) -> Job | None:
    """
    Find an existing job using the source identity.
    """

    if discovered_job.external_id and discovered_job.source_name:
        return (
            db.query(Job)
            .filter(
                Job.source_name == discovered_job.source_name,
                Job.external_id == discovered_job.external_id,
            )
            .first()
        )

    return (
        db.query(Job)
        .filter(
            Job.organization_name == discovered_job.organization_name,
            Job.title == discovered_job.title,
            Job.application_end == discovered_job.application_end,
        )
        .first()
    )