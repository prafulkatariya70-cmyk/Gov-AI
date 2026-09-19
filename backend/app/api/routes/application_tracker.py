from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.application_tracker import ApplicationTrackerRepository
from app.repositories.jobs import JobRepository
from app.schemas.application_tracker import TrackerItemCreate, TrackerItemResponse, TrackerItemUpdate, TrackerResponse

router = APIRouter(prefix="/tracker", tags=["application-tracker"])


def _response(item, job) -> TrackerItemResponse:
    return TrackerItemResponse(
        id=item.id,
        user_id=item.user_id,
        job_id=item.job_id,
        job_title=job.title,
        board_code=job.board_code,
        status=item.status,
        application_number=item.application_number,
        roll_number=item.roll_number,
        exam_center=item.exam_center,
        applied_date=item.applied_date,
        exam_date=item.exam_date or job.exam_date,
        notes=item.notes,
        reminder_enabled=item.reminder_enabled,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=TrackerResponse)
def list_tracker(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TrackerResponse:
    rows = ApplicationTrackerRepository(db).list_for_user(user.id)
    items = [_response(item, job) for item, job in rows]
    return TrackerResponse(
        saved=[item for item in items if item.status == "saved"],
        applied=[item for item in items if item.status != "saved"],
    )


@router.put("", response_model=TrackerItemResponse)
def upsert_tracker(
    payload: TrackerItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrackerItemResponse:
    job = JobRepository(db).get_by_id_or_slug(str(payload.job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    values = payload.model_dump(exclude={"job_id"}, exclude_none=True)
    item = ApplicationTrackerRepository(db).upsert(user.id, job.id, values)
    return _response(item, job)


@router.patch("/{job_id}", response_model=TrackerItemResponse)
def update_tracker(
    job_id: UUID,
    payload: TrackerItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrackerItemResponse:
    job = JobRepository(db).get_by_id_or_slug(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    values = payload.model_dump(exclude_none=True)
    item = ApplicationTrackerRepository(db).upsert(user.id, job.id, values)
    return _response(item, job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tracker(
    job_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    removed = ApplicationTrackerRepository(db).remove(user.id, job_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Tracker item not found")
