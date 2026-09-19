import os
from datetime import date

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-for-ci")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base, get_db
from app.models import Job, JobEligibility, User, UserProfile
from app.main import app


def test_personalized_eligibility_requires_authentication():
    client = TestClient(app)
    response = client.get("/api/v1/jobs/example/eligibility/me")
    assert response.status_code == 401


def test_personalized_eligibility_uses_authenticated_profile():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    app.dependency_overrides[get_db] = lambda: (yield session)
    client = TestClient(app)
    try:
        user = User(email="candidate@example.com", password_hash="x")
        session.add(user)
        session.flush()
        profile = UserProfile(user_id=user.id, full_name="Candidate", dob=date(1984, 1, 1), government_employee=True, analogous_post=True, regular_service_years=8, current_pay_level=7, parent_cadre=True, qualifying_examination=True, required_training=False, relevant_experience_years=5, experience_areas=["Cash", "Accounts", "Budget"])
        job = Job(title="Accounts Officer", slug="accounts-officer", board="SSC", board_code="SSC", job_type="Central", state="All India", status="ACTIVE")
        session.add_all([profile, job])
        session.flush()
        eligibility = JobEligibility(job_id=job.id, normalized_rules={
            "age_rules": [{"rule_type": "MAX_AGE", "value": 56, "confidence": "high"}],
            "service_rules": [{"rule_type": "GOVERNMENT_SERVICE", "value": True, "confidence": "high"}],
            "experience_rules": [{"rule_type": "MIN_EXPERIENCE_YEARS", "value": 5, "confidence": "high"}],
            "pay_rules": [{"rule_type": "PAY_LEVEL", "value": 7, "confidence": "high"}],
        })
        session.add(eligibility)
        session.commit()
        from app.core.security import create_access_token
        token = create_access_token(user.id)
        response = client.get(f"/api/v1/jobs/{job.slug}/eligibility/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["status"] == "ELIGIBLE"
        assert response.json()["confidence"] == "high"
    finally:
        app.dependency_overrides.clear()
        session.close()
