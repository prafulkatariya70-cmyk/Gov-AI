"""PostgreSQL-backed compatibility API for the preserved Expo client."""

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.eligibility import evaluate_job_eligibility
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.application import Application
from app.models.ingestion_run import IngestionRun
from app.models.job import Job
from app.models.job_source import JobSource
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.job_lifecycle import (
    application_today,
    current_or_upcoming_filter,
    lifecycle_metadata,
)

router = APIRouter(prefix="/api", tags=["Expo compatibility"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_development_user(db: Session = Depends(get_db)) -> User:
    """Temporary server-configured identity until Phase 4 authentication."""
    user = (
        db.query(User)
        .filter(
            User.email == settings.compatibility_development_user_email
        )
        .one_or_none()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Compatibility development user is not configured.",
        )

    return user


class JobEligibilitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    minimum_age: int | None = None
    maximum_age: int | None = None
    education_level: str | None = None
    degree: str | None = None
    branch: str | None = None
    qualification_text: str | None = None
    eligible_states: str | None = None
    eligible_categories: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    organization_name: str
    description: str | None = None
    official_url: str
    notification_url: str | None = None
    application_start: date | None = None
    application_end: date | None = None
    status: str
    opportunity_type: str
    source_name: str | None = None
    created_at: datetime
    lifecycle_status: str = "UNKNOWN"
    is_open: bool = False
    is_upcoming: bool = False
    is_closing_soon: bool = False
    days_until_deadline: int | None = None
    eligibility: JobEligibilitySummary | None = None


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    limit: int


class EligibilityRequirement(BaseModel):
    rule_type: str
    status: str
    required: object | None = None
    actual: object | None = None
    reason: str | None = None
    evidence: object | None = None
    confidence: str | None = None


class EligibilityResponse(BaseModel):
    job_id: int
    status: str
    confidence: str
    passed: list[EligibilityRequirement]
    failed: list[EligibilityRequirement]
    unknown: list[EligibilityRequirement]
    reasons: list[str]


class RecommendedJobResponse(JobResponse):
    eligibility_status: str
    match_score: int = Field(ge=0, le=100)
    eligibility_reasons: list[str]


class ProfileResponse(BaseModel):
    user_id: int
    full_name: str | None = None
    email: str
    date_of_birth: date | None = None
    state: str | None = None
    education_level: str | None = None
    degree: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    category: str | None = None
    experience_years: int = 0


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=150)
    date_of_birth: date | None = None
    state: str | None = Field(default=None, max_length=100)
    education_level: str | None = Field(default=None, max_length=100)
    degree: str | None = Field(default=None, max_length=150)
    branch: str | None = Field(default=None, max_length=150)
    graduation_year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )
    category: str | None = Field(default=None, max_length=50)
    experience_years: int = Field(default=0, ge=0)


class ApplicationCreateRequest(BaseModel):
    job_id: int
    status: str = Field(default="saved", max_length=50)
    notes: str | None = None
    application_number: str | None = Field(
        default=None,
        max_length=150,
    )
    roll_number: str | None = Field(
        default=None,
        max_length=150,
    )
    exam_center: str | None = Field(
        default=None,
        max_length=255,
    )
    applied_at: datetime | None = None


class ApplicationUpdateRequest(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    application_number: str | None = Field(
        default=None,
        max_length=150,
    )
    roll_number: str | None = Field(
        default=None,
        max_length=150,
    )
    exam_center: str | None = Field(
        default=None,
        max_length=255,
    )
    applied_at: datetime | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    status: str
    notes: str | None = None
    application_number: str | None = None
    roll_number: str | None = None
    exam_center: str | None = None
    applied_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    job: JobResponse | None = None


class CategorySummaryResponse(BaseModel):
    opportunity_type: str
    count: int


class IngestionSourceStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    health_status: str
    is_active: bool
    last_checked_at: datetime | None = None
    last_success_at: datetime | None = None
    last_error: str | None = None


class IngestionStatusResponse(BaseModel):
    sources: list[IngestionSourceStatus]
    latest_run_at: datetime | None = None
    jobs_count: int


def job_response(job: Job) -> JobResponse:
    data = JobResponse.model_validate(job).model_dump()
    data.update(lifecycle_metadata(job))
    return JobResponse(**data)


def profile_response(
    user: User,
    profile: UserProfile | None,
) -> ProfileResponse:
    return ProfileResponse(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        date_of_birth=profile.date_of_birth if profile else None,
        state=profile.state if profile else None,
        education_level=(
            profile.education_level if profile else None
        ),
        degree=profile.degree if profile else None,
        branch=profile.branch if profile else None,
        graduation_year=(
            profile.graduation_year if profile else None
        ),
        category=profile.category if profile else None,
        experience_years=(
            profile.experience_years if profile else 0
        ),
    )


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    search: str | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    source_name: str | None = None,
    opportunity_type: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(
        *current_or_upcoming_filter(application_today())
    )

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Job.title.ilike(term),
                Job.organization_name.ilike(term),
            )
        )

    if status_filter:
        query = query.filter(Job.status == status_filter)

    if source_name:
        query = query.filter(Job.source_name == source_name)

    if opportunity_type:
        query = query.filter(
            Job.opportunity_type == opportunity_type
        )

    total = query.count()

    jobs = (
        query.order_by(
            Job.application_end.asc().nullslast(),
            Job.created_at.desc(),
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return JobListResponse(
        items=[job_response(job) for job in jobs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/jobs/recommended",
    response_model=list[RecommendedJobResponse],
)
def recommended_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    recommended = []

    score_for = {
        "ELIGIBLE": 100,
        "NEEDS_REVIEW": 50,
        "NOT_ELIGIBLE": 0,
    }

    jobs = (
        db.query(Job)
        .filter(
            *current_or_upcoming_filter(application_today())
        )
        .order_by(Job.application_end.asc().nullslast())
        .all()
    )

    for job in jobs:
        try:
            evaluation = evaluate_job_eligibility(
                db,
                user.id,
                job.id,
            )
        except HTTPException as exc:
            # Historical/partially ingested jobs may not have normalized
            # eligibility yet; omit them rather than failing the whole feed.
            if exc.status_code in {404, 422}:
                continue
            raise

        recommended.append(
            RecommendedJobResponse(
                **job_response(job).model_dump(),
                eligibility_status=evaluation["status"],
                match_score=score_for[evaluation["status"]],
                eligibility_reasons=evaluation["reasons"],
            )
        )

    return recommended


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return job_response(job)


@router.get(
    "/jobs/{job_id}/eligibility",
    response_model=EligibilityResponse,
)
def get_job_eligibility(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    return EligibilityResponse(
        **evaluate_job_eligibility(
            db,
            user.id,
            job_id,
        )
    )


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user.id)
        .one_or_none()
    )

    return profile_response(user, profile)


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user.id)
        .one_or_none()
    )

    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    for field, value in payload.model_dump().items():
        if field == "full_name":
            user.full_name = value
        else:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile_response(user, profile)


@router.get(
    "/applications",
    response_model=list[ApplicationResponse],
)
def list_applications(
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    return [
        ApplicationResponse.model_validate(record)
        for record in (
            db.query(Application)
            .filter(Application.user_id == user.id)
            .order_by(Application.updated_at.desc())
            .all()
        )
    ]


@router.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    if db.get(Job, payload.job_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    record = Application(
        user_id=user.id,
        **payload.model_dump(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return ApplicationResponse.model_validate(record)


@router.patch(
    "/applications/{application_id}",
    response_model=ApplicationResponse,
)
def update_application(
    application_id: int,
    payload: ApplicationUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    record = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == user.id,
        )
        .one_or_none()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    for field, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return ApplicationResponse.model_validate(record)


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    record = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == user.id,
        )
        .one_or_none()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    db.delete(record)
    db.commit()


@router.get(
    "/calendar",
    response_model=list[ApplicationResponse],
)
def calendar(
    db: Session = Depends(get_db),
    user: User = Depends(get_development_user),
):
    return list_applications(db, user)


@router.get(
    "/categories-summary",
    response_model=list[CategorySummaryResponse],
)
def categories_summary(
    db: Session = Depends(get_db),
):
    """
    Return category counts for the same visible job universe
    as the main Jobs feed.

    Current/upcoming jobs are included.
    Expired and explicitly closed jobs are excluded.
    Undated jobs remain visible when the lifecycle rules allow them.
    """

    rows = (
        db.query(
            Job.opportunity_type,
            func.count(Job.id),
        )
        .filter(
            *current_or_upcoming_filter(application_today()),
            Job.opportunity_type.isnot(None),
        )
        .group_by(Job.opportunity_type)
        .order_by(Job.opportunity_type)
        .all()
    )

    return [
        CategorySummaryResponse(
            opportunity_type=kind,
            count=count,
        )
        for kind, count in rows
    ]


@router.get(
    "/ingestion/status",
    response_model=IngestionStatusResponse,
)
def ingestion_status(
    db: Session = Depends(get_db),
):
    return IngestionStatusResponse(
        sources=[
            IngestionSourceStatus.model_validate(source)
            for source in (
                db.query(JobSource)
                .order_by(JobSource.name)
                .all()
            )
        ],
        latest_run_at=db.query(
            func.max(IngestionRun.finished_at)
        ).scalar(),
        jobs_count=db.query(
            func.count(Job.id)
        ).scalar()
        or 0,
    )