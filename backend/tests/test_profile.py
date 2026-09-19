import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-for-ci")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base, get_db
from app.main import app


def _session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_profile_requires_authentication():
    client = TestClient(app)
    response = client.get("/api/v1/profile")
    assert response.status_code == 401


def test_profile_put_and_get_are_user_scoped():
    session = _session()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        register = client.post(
            "/api/v1/auth/register",
            json={"email": "profile@example.com", "password": "SecurePassword123!"},
        )
        assert register.status_code == 201
        token = register.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        missing = client.get("/api/v1/profile", headers=headers)
        assert missing.status_code == 404

        payload = {
            "full_name": "Praful Katariya",
            "dob": "2005-01-29",
            "qualification": "B.Tech",
            "degree_name": "Bachelor of Engineering",
            "stream": "Electrical and Electronics Engineering",
            "government_employee": False,
            "regular_service_years": 0,
            "current_pay_level": None,
            "relevant_experience_years": 1.5,
            "experience_areas": ["Electrical", "Analytics"],
        }
        saved = client.put("/api/v1/profile", json=payload, headers=headers)
        assert saved.status_code == 200
        assert saved.json()["full_name"] == "Praful Katariya"
        assert saved.json()["government_employee"] is False
        assert saved.json()["experience_areas"] == ["Electrical", "Analytics"]

        fetched = client.get("/api/v1/profile", headers=headers)
        assert fetched.status_code == 200
        assert fetched.json()["degree_name"] == "Bachelor of Engineering"
        assert fetched.json()["relevant_experience_years"] == 1.5
    finally:
        app.dependency_overrides.clear()
        session.close()
