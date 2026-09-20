from datetime import datetime

from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.job_source import JobSource
from app.services.ingestion.registry import get_adapter
from app.services.ingestion.source_monitor import (
    get_sources_due_for_check,
)
from app.services.ingestion.pipeline import run_ingestion


def run_source(
    db: Session,
    source: JobSource,
) -> IngestionRun:
    """
    Run ingestion for one source and record the result.
    """

    started_at = datetime.utcnow()

    ingestion_run = IngestionRun(
        source_id=source.id,
        started_at=started_at,
        status="running",
    )

    db.add(ingestion_run)
    db.flush()

    try:
        adapter = get_adapter(
            source.name
        )

        stats = run_ingestion(
            db=db,
            adapter=adapter,
        )

        finished_at = datetime.utcnow()

        ingestion_run.discovered = stats.discovered
        ingestion_run.created = stats.created
        ingestion_run.updated = stats.updated
        ingestion_run.skipped = stats.skipped
        ingestion_run.failed = stats.failed
        ingestion_run.finished_at = finished_at

        source.last_checked_at = finished_at

        if stats.failed > 0:
            ingestion_run.status = "completed_with_errors"

            source.health_status = "degraded"

            source.last_error = (
                f"{stats.failed} job(s) failed during ingestion."
            )

        else:
            ingestion_run.status = "success"

            source.health_status = "healthy"

            source.last_error = None

            source.last_success_at = finished_at

        db.commit()

        return ingestion_run

    except Exception as exc:

        db.rollback()

        finished_at = datetime.utcnow()

        source.last_checked_at = finished_at
        source.health_status = "failed"
        source.last_error = str(exc)

        failed_run = IngestionRun(
            source_id=source.id,
            started_at=started_at,
            finished_at=finished_at,
            status="failed",
            error_message=str(exc),
        )

        db.add(failed_run)

        db.commit()

        return failed_run


def run_due_sources(
    db: Session,
) -> list[IngestionRun]:
    """
    Run ingestion for every active source that is due.
    """

    sources = get_sources_due_for_check(
        db
    )

    results: list[IngestionRun] = []

    for source in sources:

        result = run_source(
            db=db,
            source=source,
        )

        results.append(result)

    return results
