from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.config import get_settings
from app.models.user import User
from app.services.jobs.ingestion_cycle import IngestionCycleService
from app.services.jobs.official_sources import seed_official_sources

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("")
def trigger_sync(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run one bounded official-source ingestion cycle for an authenticated user."""
    del user
    seed_official_sources(db)
    result = IngestionCycleService(db).run(process_limit=10)
    return {
        "message": "Official government job sync completed.",
        "sources_checked": result.sources_checked,
        "notifications_queued": result.notifications_queued,
        "notifications_processed": result.notifications_processed,
    }


@router.post("/internal")
def trigger_internal_sync(
    x_ingestion_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Run scheduled ingestion using a dedicated machine-to-machine secret."""
    settings = get_settings()
    if not x_ingestion_token or x_ingestion_token != settings.ingestion_sync_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ingestion token.")
    seed_official_sources(db)
    result = IngestionCycleService(db).run(process_limit=10)
    return {
        "message": "Scheduled official government job sync completed.",
        "sources_checked": result.sources_checked,
        "notifications_queued": result.notifications_queued,
        "notifications_processed": result.notifications_processed,
    }
