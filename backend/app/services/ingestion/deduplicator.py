import hashlib

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.job import Job
from app.services.ingestion.models import DiscoveredJob


def normalize_text(value: str | None) -> str:
    """
    Normalize text for reliable identity comparisons.
    """
    if not value:
        return ""

    return " ".join(value.lower().split())


def build_job_fingerprint(job: DiscoveredJob) -> str:
    """
    Build a deterministic source-scoped fingerprint.

    Identity preference:
    1. Source + external ID.
    2. Source + notification URL.
    3. Source + organization + title + application end date.
    """
    source = normalize_text(job.source_name)

    if job.external_id:
        raw_value = (
            f"{source}|"
            f"external-id|"
            f"{normalize_text(job.external_id)}"
        )
    elif job.notification_url:
        raw_value = (
            f"{source}|"
            f"notification-url|"
            f"{normalize_text(job.notification_url)}"
        )
    else:
        raw_value = (
            f"{source}|"
            f"fallback|"
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
    Find an existing job using the strongest available identity.

    The lookup is always source-scoped when source information exists,
    preventing cross-source collisions.
    """
    source_name = discovered_job.source_name

    if discovered_job.external_id and source_name:
        existing = (
            db.query(Job)
            .filter(
                func.lower(Job.source_name)
                == normalize_text(source_name),
                func.lower(Job.external_id)
                == normalize_text(discovered_job.external_id),
            )
            .first()
        )

        if existing:
            return existing

    if discovered_job.notification_url and source_name:
        existing = (
            db.query(Job)
            .filter(
                func.lower(Job.source_name)
                == normalize_text(source_name),
                Job.notification_url
                == discovered_job.notification_url,
            )
            .first()
        )

        if existing:
            return existing

    fallback_filters = [
        Job.organization_name == discovered_job.organization_name,
        Job.title == discovered_job.title,
        Job.application_end == discovered_job.application_end,
    ]

    if source_name:
        fallback_filters.append(
            func.lower(Job.source_name)
            == normalize_text(source_name)
        )

    return (
        db.query(Job)
        .filter(*fallback_filters)
        .first()
    )
