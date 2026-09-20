from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.compatibility import get_db
from app.api.compatibility import router as compatibility_router
from app.core.config import settings
from app.models import (
    Application,
    Base,
    IngestionRun,
    Job,
    JobEligibility,
    JobSource,
    User,
    UserProfile,
)

app = FastAPI()
app.include_router(compatibility_router)


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = Session()

    user = User(
        email=settings.compatibility_development_user_email,
        password_hash="not-used",
        full_name="Development User",
    )

    job = Job(
        organization_name="Staff Selection Commission",
        title="Graduate Recruitment",
        description="A real persisted job record.",
        official_url="https://example.gov/apply",
        notification_url="https://example.gov/notice.pdf",
        application_start=date(2026, 1, 1),
        application_end=date(2026, 12, 31),
        status="active",
        opportunity_type="PUBLIC_RECRUITMENT",
        source_name="SSC",
    )

    source = JobSource(
        name="SSC",
        base_url="https://example.gov",
        source_type="html",
    )

    expired = Job(
        organization_name="Old Commission",
        title="Expired Recruitment",
        official_url="https://example.gov/old",
        application_end=date(2026, 1, 1),
        status="active",
        opportunity_type="PUBLIC_RECRUITMENT",
    )

    closed = Job(
        organization_name="Closed Commission",
        title="Closed Recruitment",
        official_url="https://example.gov/closed",
        application_end=date(2026, 12, 31),
        status="closed",
        opportunity_type="PUBLIC_RECRUITMENT",
    )

    upcoming = Job(
        organization_name="Future Commission",
        title="Upcoming Recruitment",
        official_url="https://example.gov/future",
        application_start=date(2026, 12, 1),
        application_end=date(2026, 12, 31),
        status="active",
        opportunity_type="PUBLIC_RECRUITMENT",
    )

    undated = Job(
        organization_name="Deputation Commission",
        title="Undated Deputation",
        official_url="https://example.gov/undated",
        status="active",
        opportunity_type="DEPUTATION",
    )

    session.add_all(
        [
            user,
            job,
            source,
            expired,
            closed,
            upcoming,
            undated,
        ]
    )

    session.flush()

    session.add(
        UserProfile(
            user_id=user.id,
            date_of_birth=date(1995, 5, 1),
            education_level="Graduate",
            experience_years=4,
        )
    )

    session.add(
        JobEligibility(
            job_id=job.id,
            normalized_rules={
                "age_rules": [],
                "service_rules": [],
                "qualification_rules": [],
                "experience_rules": [],
                "department_rules": [],
                "special_rules": [],
                "pay_rules": [],
            },
        )
    )

    session.add(
        IngestionRun(
            source_id=source.id,
            status="success",
        )
    )

    session.commit()

    def override_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as test_client:
        yield test_client, job.id

    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(engine)


def test_jobs_profile_categories_and_ingestion_status(client):
    test_client, job_id = client

    jobs = test_client.get(
        "/api/jobs",
        params={"search": "Graduate"},
    )

    assert jobs.status_code == 200
    assert jobs.json()["total"] == 1
    assert jobs.json()["items"][0]["id"] == job_id

    public_feed = test_client.get("/api/jobs")

    assert public_feed.status_code == 200

    titles = {
        item["title"]
        for item in public_feed.json()["items"]
    }

    assert "Expired Recruitment" not in titles
    assert "Closed Recruitment" not in titles
    assert "Upcoming Recruitment" in titles
    assert "Undated Deputation" in titles

    detail = test_client.get(
        f"/api/jobs/{job_id}"
    )

    assert detail.status_code == 200
    assert (
        detail.json()["organization_name"]
        == "Staff Selection Commission"
    )

    profile = test_client.get("/api/profile")

    assert profile.status_code == 200
    assert profile.json()["full_name"] == "Development User"

    updated = test_client.put(
        "/api/profile",
        json={
            "full_name": "Updated User",
            "state": "Karnataka",
            "experience_years": 5,
        },
    )

    assert updated.status_code == 200
    assert updated.json()["state"] == "Karnataka"

    categories = test_client.get(
        "/api/categories-summary"
    )

    assert categories.status_code == 200

    assert sorted(
        categories.json(),
        key=lambda item: item["opportunity_type"],
    ) == [
        {
            "opportunity_type": "DEPUTATION",
            "count": 1,
        },
        {
            "opportunity_type": "PUBLIC_RECRUITMENT",
            "count": 2,
        },
    ]

    status = test_client.get(
        "/api/ingestion/status"
    )

    assert status.status_code == 200
    # Ingestion status counts all persisted job records, including
    # expired and closed history that the public feed intentionally hides.
    assert status.json()["jobs_count"] == 5
    assert status.json()["sources"][0]["name"] == "SSC"


def test_recommendations_eligibility_and_application_lifecycle(client):
    test_client, job_id = client

    eligibility = test_client.get(
        f"/api/jobs/{job_id}/eligibility"
    )

    assert eligibility.status_code == 200
    assert eligibility.json()["status"] == "NEEDS_REVIEW"

    recommendations = test_client.get(
        "/api/jobs/recommended"
    )

    assert recommendations.status_code == 200
    assert recommendations.json()[0]["match_score"] == 50

    created = test_client.post(
        "/api/applications",
        json={
            "job_id": job_id,
            "status": "applied",
            "application_number": "APP-1",
        },
    )

    assert created.status_code == 201

    application_id = created.json()["id"]

    assert len(
        test_client.get(
            "/api/applications"
        ).json()
    ) == 1

    patched = test_client.patch(
        f"/api/applications/{application_id}",
        json={
            "status": "exam_scheduled",
        },
    )

    assert patched.status_code == 200
    assert patched.json()["status"] == "exam_scheduled"

    assert len(
        test_client.get(
            "/api/calendar"
        ).json()
    ) == 1

    deleted = test_client.delete(
        f"/api/applications/{application_id}"
    )

    assert deleted.status_code == 204

    assert test_client.get(
        "/api/applications"
    ).json() == []