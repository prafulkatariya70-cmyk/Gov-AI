from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.job_eligibility import JobEligibility
from app.models.user_profile import UserProfile
from app.services.eligibility.adapter import (
    user_profile_to_candidate_profile,
)
from app.services.eligibility.evaluator import (
    EligibilityEvaluator,
)
from app.services.eligibility.serialization import (
    normalized_eligibility_from_dict,
)


router = APIRouter(
    prefix="/eligibility",
    tags=["Eligibility"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def eligibility_health():
    return {
        "status": "eligibility service running"
    }


def evaluate_job_eligibility(db: Session, user_id: int, job_id: int) -> dict:
    # =========================================================
    # USER PROFILE
    # =========================================================

    profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.user_id == user_id
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="User profile not found.",
        )

    # =========================================================
    # JOB ELIGIBILITY
    # =========================================================

    requirements = (
        db.query(JobEligibility)
        .filter(
            JobEligibility.job_id == job_id
        )
        .first()
    )

    if requirements is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Job eligibility requirements "
                "not found."
            ),
        )

    # =========================================================
    # NORMALIZED RULES
    # =========================================================

    if not requirements.normalized_rules:
        raise HTTPException(
            status_code=422,
            detail=(
                "Normalized eligibility rules are "
                "not available for this job."
            ),
        )

    try:
        normalized = (
            normalized_eligibility_from_dict(
                requirements.normalized_rules
            )
        )

    except (
        TypeError,
        ValueError,
        AttributeError,
    ) as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Stored eligibility rules are invalid."
            ),
        ) from exc

    # =========================================================
    # CANDIDATE ADAPTER
    # =========================================================

    candidate = (
        user_profile_to_candidate_profile(
            profile
        )
    )

    # =========================================================
    # EVALUATION
    # =========================================================

    evaluator = EligibilityEvaluator()

    result = evaluator.evaluate(
        candidate=candidate,
        rules=normalized,
    )

    # =========================================================
    # RESPONSE
    # =========================================================

    return {
        "user_id": user_id,
        "job_id": job_id,
        "status": result.status,
        "confidence": result.confidence,
        "passed": [
            {
                "rule_type": item.rule_type,
                "status": item.status,
                "required": item.required,
                "actual": item.actual,
                "reason": item.reason,
                "evidence": item.evidence,
                "confidence": item.confidence,
            }
            for item in result.passed
        ],
        "failed": [
            {
                "rule_type": item.rule_type,
                "status": item.status,
                "required": item.required,
                "actual": item.actual,
                "reason": item.reason,
                "evidence": item.evidence,
                "confidence": item.confidence,
            }
            for item in result.failed
        ],
        "unknown": [
            {
                "rule_type": item.rule_type,
                "status": item.status,
                "required": item.required,
                "actual": item.actual,
                "reason": item.reason,
                "evidence": item.evidence,
                "confidence": item.confidence,
            }
            for item in result.unknown
        ],
        "reasons": result.reasons,
    }


@router.get("/check/{user_id}/{job_id}")
def check_job_eligibility(
    user_id: int,
    job_id: int,
    db: Session = Depends(get_db),
):
    """Legacy evaluator endpoint retained for existing callers."""
    return evaluate_job_eligibility(db, user_id, job_id)
