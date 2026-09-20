from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.documents.extractor import PDFTextExtractor
from app.services.documents.fetcher import DocumentFetcher
from app.services.documents.parsing.notification_parser import (
    NotificationParser,
)
from app.services.eligibility.persistence import (
    save_parsed_eligibility,
)
from app.services.ingestion.base_adapter import JobSourceAdapter
from app.services.ingestion.job_persistence import save_discovered_job
from app.services.ingestion.models import DiscoveredJob


@dataclass
class IngestionStats:
    discovered: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    eligibility_created: int = 0
    eligibility_updated: int = 0
    eligibility_failed: int = 0


def validate_job(job: DiscoveredJob) -> bool:
    """
    Validate the minimum information required to store a job.
    """

    if not job.organization_name:
        return False

    if not job.title:
        return False

    if not job.official_url:
        return False

    return True


def _parse_and_save_eligibility(
    db: Session,
    job,
) -> str:
    """
    Fetch, extract, parse, and persist notification eligibility.

    Returns:
        "created"
        "updated"
        "unchanged"
        "failed"
        "unavailable"
    """

    notification_url = getattr(
        job,
        "notification_url",
        None,
    )

    if not notification_url:
        return "unavailable"

    try:
        # ------------------------------------------------------------
        # Fetch notification
        # ------------------------------------------------------------

        fetcher = DocumentFetcher()

        fetched_document = fetcher.fetch(
            notification_url,
        )

        if not fetched_document:
            return "failed"

        # ------------------------------------------------------------
        # Extract PDF text
        # ------------------------------------------------------------

        extractor = PDFTextExtractor()

        extracted_document = extractor.extract(
            fetched_document.content,
        )

        if not extracted_document:
            return "failed"

        text = getattr(
            extracted_document,
            "text",
            None,
        )

        if not text:
            return "failed"

        # ------------------------------------------------------------
        # Parse notification
        # ------------------------------------------------------------

        parser = NotificationParser()

        parsed_notification = parser.parse(
            text,
        )

        # ------------------------------------------------------------
        # Check whether an eligibility record already exists
        # ------------------------------------------------------------

        existing_eligibility = job.eligibility

        # ------------------------------------------------------------
        # Persist parsed eligibility
        # ------------------------------------------------------------

        save_parsed_eligibility(
            db,
            job,
            parsed_notification,
        )

        if existing_eligibility is None:
            return "created"

        return "updated"

    except Exception as exc:
        print(
            "Eligibility processing error: "
            f"{exc}"
        )

        return "failed"


def run_ingestion(
    db: Session,
    adapter: JobSourceAdapter,
) -> IngestionStats:
    """
    Run discovery, validation, deduplication,
    job persistence, and eligibility processing.
    """

    stats = IngestionStats()

    discovered_jobs = adapter.discover_jobs()

    stats.discovered = len(discovered_jobs)

    for discovered_job in discovered_jobs:

        if not validate_job(discovered_job):
            stats.skipped += 1
            continue

        try:
            saved_job, action = save_discovered_job(
                db,
                discovered_job,
            )

            # --------------------------------------------------------
            # Job persistence statistics
            # --------------------------------------------------------

            if action == "created":
                stats.created += 1

            elif action == "updated":
                stats.updated += 1

            elif action == "skipped":
                stats.skipped += 1

            # --------------------------------------------------------
            # Eligibility processing
            # --------------------------------------------------------

            eligibility_action = _parse_and_save_eligibility(
                db,
                saved_job,
            )

            if eligibility_action == "created":
                stats.eligibility_created += 1

            elif eligibility_action == "updated":
                stats.eligibility_updated += 1

            elif eligibility_action == "failed":
                stats.eligibility_failed += 1

        except Exception as exc:
            db.rollback()

            stats.failed += 1

            print(
                "Ingestion error: "
                f"{exc}"
            )

    db.commit()

    return stats