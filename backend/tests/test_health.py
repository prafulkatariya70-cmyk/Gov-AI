import os
os.environ.setdefault("DATABASE_URL","sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET","test-secret-for-ci")
os.environ.setdefault("INGESTION_SYNC_TOKEN","ci-ingestion-secret-01234567890123456789")
from fastapi.testclient import TestClient
from app.main import app

def test_liveness_health():
    response=TestClient(app).get("/api/v1/health")
    assert response.status_code==200
    assert response.json()=={"status":"ok"}
