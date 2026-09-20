from sqlalchemy.orm import Session

from app.models.job import Job
from app.services.ingestion.deduplicator import find_existing_job
from app.services.ingestion.models import DiscoveredJob


def create_job(
    db: Session,
    discovered_job: DiscoveredJob,
) -> Job:
    """
    Create a new job from discovered source data.
    """

    job = Job(
        organization_name=discovered_job.organization_name,
        title=discovered_job.title,
        description=discovered_job.description,
        official_url=discovered_job.official_url,
        notification_url=discovered_job.notification_url,
        application_start=discovered_job.application_start,
        application_end=discovered_job.application_end,
        status="active",
        source_name=discovered_job.source_name,
        external_id=discovered_job.external_id,
        opportunity_type=discovered_job.opportunity_type,
    )

    db.add(job)
    db.flush()

    return job


def job_has_changes(
    job: Job,
    discovered_job: DiscoveredJob,
) -> bool:
    """
    Determine whether newly discovered data differs
    from the existing database record.
    """

    return any(
        [
            job.organization_name
            != discovered_job.organization_name,

            job.title
            != discovered_job.title,

            job.description
            != discovered_job.description,

            job.official_url
            != discovered_job.official_url,

            job.notification_url
            != discovered_job.notification_url,

            job.application_start
            != discovered_job.application_start,

            job.application_end
            != discovered_job.application_end,

            job.source_name
            != discovered_job.source_name,

            job.external_id
            != discovered_job.external_id,

            job.opportunity_type
            != discovered_job.opportunity_type,
        ]
    )


def update_job(
    job: Job,
    discovered_job: DiscoveredJob,
) -> Job:
    """
    Update an existing job with newly discovered information.
    """

    job.organization_name = discovered_job.organization_name
    job.title = discovered_job.title
    job.description = discovered_job.description
    job.official_url = discovered_job.official_url
    job.notification_url = discovered_job.notification_url
    job.application_start = discovered_job.application_start
    job.application_end = discovered_job.application_end
    job.source_name = discovered_job.source_name
    job.external_id = discovered_job.external_id
    job.opportunity_type = discovered_job.opportunity_type

    return job


def save_discovered_job(
    db: Session,
    discovered_job: DiscoveredJob,
) -> tuple[Job, str]:
    """
    Create, update, or skip a discovered job.

    Returns:
        (job, action)

    action values:
        "created" -> new job
        "updated" -> existing job changed
        "skipped" -> existing job unchanged
    """

    existing_job = find_existing_job(
        db,
        discovered_job,
    )

    if existing_job:

        if not job_has_changes(
            existing_job,
            discovered_job,
        ):
            return existing_job, "skipped"

        updated_job = update_job(
            existing_job,
            discovered_job,
        )

        db.flush()

        return updated_job, "updated"

    new_job = create_job(
        db,
        discovered_job,
    )

    return new_job, "created"