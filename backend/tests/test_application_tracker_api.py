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
from app.models import Job


def _session():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def _job(session):
    job = Job(
        title="Data Analyst", slug="data-analyst-"+uuid4().hex, board="Test Board", board_code="TEST",
        job_type="Central", state="All India", category="Engineering", post_name="Data Analyst",
        total_vacancies=10, status="Open", is_featured=False, is_new_today=False, is_closing_soon=False,
        start_date=date(2026, 9, 1), last_date=date(2026, 10, 1), official_website_url="https://example.gov"
    )
    session.add(job); session.commit(); return job


def test_application_tracker_is_user_scoped_and_upserted():
    session = _session()
    app.dependency_overrides[get_db] = lambda: (yield session)
    client = TestClient(app)
    try:
        register = client.post("/api/v1/auth/register", json={"email":"tracker@example.com","password":"SecurePassword123!"})
        assert register.status_code == 201
        headers = {"Authorization": "Bearer " + register.json()["access_token"]}
        job = _job(session)

        saved = client.put("/api/v1/tracker", json={"job_id": str(job.id), "status":"saved"}, headers=headers)
        assert saved.status_code == 200
        assert saved.json()["status"] == "saved"
        assert saved.json()["job_title"] == "Data Analyst"

        updated = client.patch("/api/v1/tracker/" + str(job.id), json={"status":"applied","application_number":"APP-123","applied_date":"2026-09-19"}, headers=headers)
        assert updated.status_code == 200
        assert updated.json()["status"] == "applied"
        assert updated.json()["application_number"] == "APP-123"

        listing = client.get("/api/v1/tracker", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["saved"] == []
        assert len(listing.json()["applied"]) == 1

        removed = client.delete("/api/v1/tracker/" + str(job.id), headers=headers)
        assert removed.status_code == 204
        assert client.get("/api/v1/tracker", headers=headers).json() == {"saved": [], "applied": []}
    finally:
        app.dependency_overrides.clear(); session.close()
