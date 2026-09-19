import os
from datetime import date
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-for-ci")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Job, JobEligibility


def _session():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def _seed_job(session: Session) -> Job:
    job = Job(
        title="Assistant Provident Fund Commissioner",
        slug=f"assistant-provident-fund-commissioner-{uuid4().hex}",
        board="Union Public Service Commission",
        board_code="UPSC",
        job_type="Central",
        state="All India",
        category="Finance",
        post_name="Assistant Provident Fund Commissioner",
        total_vacancies=80,
        qualification_required="Degree",
        min_age=21,
        max_age=35,
        notification_date=date(2026, 8, 22),
        start_date=date(2026, 8, 22),
        last_date=date(2026, 9, 11),
        official_apply_url="https://example.gov/apply",
        official_notification_pdf_url="https://example.gov/notification.pdf",
        official_website_url="https://example.gov",
        salary_scale="Pay Level-10",
        status="Closed",
        is_featured=False,
        is_new_today=False,
        is_closing_soon=False,
    )
    session.add(job)
    session.flush()
    session.add(
        JobEligibility(
            job_id=job.id,
            normalized_rules={
                "age_rules": [
                    {
                        "rule_type": "MAXIMUM_AGE",
                        "value": 35,
                        "confidence": "high",
                        "evidence": "Age limit 35 years",
                    }
                ]
            },
            qualification_text="Degree",
        )
    )
    session.commit()
    return job


def test_health_and_jobs_api_contract():
    session = _session()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        job = _seed_job(session)
        response = client.get("/api/v1/jobs", params={"search": "Provident", "page": 1, "page_size": 20})
        assert response.status_code == 200

        body = response.json()
        assert body["count"] == 1
        assert body["page"] == 1
        assert body["page_size"] == 20
        assert body["jobs"][0]["id"] == str(job.id)
        assert body["jobs"][0]["board_code"] == "UPSC"
        assert body["jobs"][0]["total_vacancies"] == 80
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_job_detail_and_eligibility_requirements_api_contract():
    session = _session()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        job = _seed_job(session)

        detail = client.get(f"/api/v1/jobs/{job.slug}")
        assert detail.status_code == 200
        assert detail.json()["slug"] == job.slug
        assert detail.json()["title"] == "Assistant Provident Fund Commissioner"

        requirements = client.get(f"/api/v1/jobs/{job.id}/eligibility")
        assert requirements.status_code == 200
        assert requirements.json()["job_id"] == str(job.id)
        assert requirements.json()["normalized_rules"]["age_rules"][0]["value"] == 35

        missing = client.get("/api/v1/jobs/does-not-exist")
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_authenticated_job_eligibility_api_contract():
    session = _session()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        job = _seed_job(session)
        register = client.post(
            "/api/v1/auth/register",
            json={"email": "eligibility@example.com", "password": "SecurePassword123!"},
        )
        assert register.status_code == 201
        token = register.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        profile = client.put(
            "/api/v1/profile",
            json={
                "full_name": "Eligibility Candidate",
                "dob": "2005-01-29",
                "qualification": "Degree",
            },
            headers=headers,
        )
        assert profile.status_code == 200

        decision = client.get(
            f"/api/v1/jobs/{job.slug}/eligibility/me",
            headers=headers,
        )
        assert decision.status_code == 200
        body = decision.json()
        assert body["status"] in {"ELIGIBLE", "NEEDS_REVIEW", "NOT_ELIGIBLE"}
        assert "reasons" in body
        assert "evidence" in body
    finally:
        app.dependency_overrides.clear()
        session.close()
