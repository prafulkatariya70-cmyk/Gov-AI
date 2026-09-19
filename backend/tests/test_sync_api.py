import os
os.environ.setdefault("DATABASE_URL","sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET","test-secret-for-ci")
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.core.database import Base,get_db
from app.main import app


def test_sync_requires_authentication():
    client=TestClient(app)
    response=client.post("/api/v1/sync")
    assert response.status_code == 401


def test_sync_route_runs_bounded_cycle():
    session=Session(create_engine("sqlite+pysqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool))
    Base.metadata.create_all(session.bind)
    app.dependency_overrides[get_db]=lambda:(yield session)
    client=TestClient(app)
    try:
        register=client.post("/api/v1/auth/register",json={"email":"sync@example.com","password":"SecurePassword123!"})
        assert register.status_code==201
        token=register.json()["access_token"]
        import app.api.routes.sync as sync_route
        class FakeCycle:
            def __init__(self,db): pass
            def run(self,process_limit=10):
                class R: sources_checked=2; notifications_queued=3; notifications_processed=3
                assert process_limit==10
                return R()
        original=sync_route.IngestionCycleService
        sync_route.IngestionCycleService=FakeCycle
        try:
            response=client.post("/api/v1/sync",headers={"Authorization":"Bearer "+token})
        finally:
            sync_route.IngestionCycleService=original
        assert response.status_code==200
        assert response.json()["notifications_processed"]==3
    finally:
        app.dependency_overrides.clear();session.close()
