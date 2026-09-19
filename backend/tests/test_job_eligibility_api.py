import os
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Job, JobEligibility
from app.repositories.job_eligibility import JobEligibilityRepository


def _session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_job_eligibility_repository_returns_persisted_rules():
    with _session() as session:
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

        eligibility = JobEligibility(
            job_id=job.id,
            normalized_rules={
                "age_rules": [
                    {
                        "rule_type": "MAXIMUM_AGE",
                        "value": 56,
                        "confidence": "high",
                        "evidence": "Age limit 56 years",
                    }
                ]
            },
            qualification_text="Relevant accounting qualification",
            experience_requirement="Five years' experience",
        )
        session.add(eligibility)
        session.commit()

        stored = JobEligibilityRepository(session).get_by_job_id(job.id)

        assert stored is not None
        assert stored.normalized_rules["age_rules"][0]["value"] == 56
        assert stored.experience_requirement == "Five years' experience"


def test_job_eligibility_repository_returns_none_when_missing():
    with _session() as session:
        assert JobEligibilityRepository(session).get_by_job_id(uuid4()) is None
