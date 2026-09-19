from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.job_eligibility import JobEligibilityRepository
from app.repositories.jobs import JobRepository
from app.schemas.job import JobEligibilityResponse, JobListResponse, JobSummary

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    job_type: str | None = None,
    state: str | None = None,
    qualification: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> JobListResponse:
    total, jobs = JobRepository(db).list_jobs(
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        job_type=job_type,
        state=state,
        qualification=qualification,
        status=status,
    )
    return JobListResponse(count=total, page=page, page_size=page_size, jobs=jobs)


@router.get("/{identifier}/eligibility", response_model=JobEligibilityResponse)
def get_job_eligibility(
    identifier: str,
    db: Session = Depends(get_db),
) -> JobEligibilityResponse:
    job = JobRepository(db).get_by_id_or_slug(identifier)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    eligibility = JobEligibilityRepository(db).get_by_job_id(job.id)
    if not eligibility:
        raise HTTPException(
            status_code=404,
            detail="Eligibility requirements not available for this job",
        )

    return eligibility


@router.get("/{identifier}", response_model=JobSummary)
def get_job(identifier: str, db: Session = Depends(get_db)) -> JobSummary:
    job = JobRepository(db).get_by_id_or_slug(identifier)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job
