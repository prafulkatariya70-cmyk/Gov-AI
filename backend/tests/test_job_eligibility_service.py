import os
from datetime import date
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Job, JobEligibility, User, UserProfile
from app.services.eligibility.job_service import PersistedEligibilityService


def _session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def _seed_job(session: Session, rules: dict):
    job = Job(
        title="Accounts Officer",
        slug=f"accounts-officer-{uuid4().hex}",
        board="Staff Selection Commission",
        board_code="SSC",
        job_type="Deputation",
        state="All India",
        category="Finance",
        post_name="Accounts Officer",
        total_vacancies=4,
        status="Open",
    )
    session.add(job)
    session.flush()
    session.add(JobEligibility(job_id=job.id, normalized_rules=rules))
    return job


def _seed_user(session: Session, dob: date | None):
    user = User(email=f"test-{uuid4().hex}@example.com")
    session.add(user)
    session.flush()
    session.add(UserProfile(user_id=user.id, full_name="Test Candidate", dob=dob))
    session.flush()
    return user


def test_persisted_rules_are_reconstructed_and_evaluated():
    with _session() as session:
        job = _seed_job(session, {
            "age_rules": [
                {"rule_type": "MINIMUM_AGE", "value": 18, "confidence": "high", "evidence": "Age 18+"},
                {"rule_type": "MAXIMUM_AGE", "value": 30, "confidence": "high", "evidence": "Age up to 30"},
            ]
        })
        user = _seed_user(session, date(2000, 1, 1))
        session.commit()

        result = PersistedEligibilityService(session).evaluate(job.id, user.id)

        assert result.status == "ELIGIBLE"
        assert result.confidence == "high"
        assert result.failed_requirements == []
        assert len(result.evidence) == 2


def test_missing_candidate_data_is_needs_review_not_ineligible():
    with _session() as session:
        job = _seed_job(session, {
            "age_rules": [
                {"rule_type": "MINIMUM_AGE", "value": 18, "confidence": "high", "evidence": "Age 18+"}
            ]
        })
        user = _seed_user(session, None)
        session.commit()

        result = PersistedEligibilityService(session).evaluate(job.id, user.id)

        assert result.status == "NEEDS_REVIEW"
        assert result.unknown_requirements
        assert not result.failed_requirements


def test_missing_eligibility_rules_requires_review():
    with _session() as session:
        job = _seed_job(session, {})
        user = _seed_user(session, date(2000, 1, 1))
        session.commit()

        result = PersistedEligibilityService(session).evaluate(job.id, user.id)

        assert result.status == "NEEDS_REVIEW"
        assert result.confidence == "low"


def test_age_calculation_handles_birthday_boundary():
    assert PersistedEligibilityService._calculate_age(date(2000, 9, 20), date(2026, 9, 19)) == 25
    assert PersistedEligibilityService._calculate_age(date(2000, 9, 19), date(2026, 9, 19)) == 26


def test_full_profile_fields_reach_candidate_contract():
    with _session() as session:
        user = _seed_user(session, date(2000, 1, 1))
        profile = session.get(UserProfile, user.id) if False else None
        stored = session.query(UserProfile).filter_by(user_id=user.id).one()
        candidate = PersistedEligibilityService._to_candidate(stored)

        assert candidate.government_employee is True
        assert candidate.analogous_post is True
        assert candidate.regular_service_years == 8
        assert candidate.current_pay_level == 7
        assert candidate.parent_cadre is True
        assert candidate.qualifying_examination is True
        assert candidate.required_training is False
        assert candidate.relevant_experience_years == 5
        assert candidate.experience_areas == ["Cash", "Accounts", "Budget"]
