import os
os.environ.setdefault("DATABASE_URL","sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET","test-secret-for-ci")
os.environ.setdefault("INGESTION_SYNC_TOKEN","0123456789abcdef0123456789abcdef")
from fastapi.testclient import TestClient
from app.main import app

def test_internal_sync_rejects_missing_token():
    client=TestClient(app)
    assert client.post("/api/v1/sync/internal").status_code==401

def test_internal_sync_rejects_wrong_token():
    client=TestClient(app)
    assert client.post("/api/v1/sync/internal",headers={"X-Ingestion-Token":"wrong"}).status_code==401
