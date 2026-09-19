import os
from uuid import UUID

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-for-ci")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from app.core.database import Base, get_db
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.main import app


def _session():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_password_hash_round_trip():
    password = "SecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_jwt_round_trip():
    user_id = UUID("11111111-1111-1111-1111-111111111111")
    token = create_access_token(user_id)
    assert decode_access_token(token) == user_id


def test_auth_routes_register_login_and_me():
    session = _session()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    try:
        register = client.post(
            "/api/v1/auth/register",
            json={"email": "Test@Example.com", "password": "SecurePassword123!"},
        )
        assert register.status_code == 201
        body = register.json()
        assert body["user"]["email"] == "test@example.com"
        token = body["access_token"]

        me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200
        assert me.json()["email"] == "test@example.com"

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "TEST@example.com", "password": "SecurePassword123!"},
        )
        assert login.status_code == 200
        assert login.json()["user"]["id"] == body["user"]["id"]

        duplicate = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "AnotherPassword123!"},
        )
        assert duplicate.status_code == 409

        invalid = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong-password"},
        )
        assert invalid.status_code == 401

        unauthenticated = client.get("/api/v1/auth/me")
        assert unauthenticated.status_code == 401
    finally:
        app.dependency_overrides.clear()
        session.close()
