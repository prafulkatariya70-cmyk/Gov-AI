import os

import pytest
import requests

pytestmark = pytest.mark.integration

BASE_URL = os.environ.get("EXPO_BACKEND_URL") or os.environ.get("EXPO_PUBLIC_BACKEND_URL")
if not BASE_URL:
    pytest.skip(
        "Portal integration tests require EXPO_BACKEND_URL or EXPO_PUBLIC_BACKEND_URL.",
        allow_module_level=True,
    )

BASE_URL = BASE_URL.rstrip("/")
USER = "demo_candidate"


def test_jobs_search_filter_sort():
    response = requests.get(f"{BASE_URL}/api/jobs", params={"search": "SSC", "category": "Staff Selection", "job_type": "Central", "sort_by": "closing_soon", "user_id": USER})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert all("SSC" in job["title"] or "SSC" in job.get("board_code", "") for job in data["jobs"])


def test_recommended_contains_match_breakdowns():
    response = requests.get(f"{BASE_URL}/api/jobs/recommended", params={"user_id": USER})
    assert response.status_code == 200
    data = response.json()
    assert data["candidate"]["user_id"] == USER
    jobs = data["high_match_jobs"] + data["eligible_jobs"] + data["need_attention_jobs"]
    assert jobs and all("match_info" in job and "match_percentage" in job["match_info"] for job in jobs)


def test_sync_check_returns_ingestion_summary():
    response = requests.post(f"{BASE_URL}/api/jobs/sync-check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_active_jobs"] >= 1
    assert data["synced_at"]


def test_profile_update_recalculates_age():
    original = requests.get(f"{BASE_URL}/api/profile", params={"user_id": USER}).json()
    response = requests.post(f"{BASE_URL}/api/profile", params={"user_id": USER}, json={"dob": "1990-01-01", "category": "SC", "domicile_state": "Bihar", "qualification": "Graduate"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["category"] == "SC" and updated["domicile_state"] == "Bihar"
    assert updated["age"] >= 35
    requests.post(f"{BASE_URL}/api/profile", params={"user_id": USER}, json={"dob": original["dob"], "category": original["category"], "domicile_state": original["domicile_state"], "qualification": original["qualification"]})


def test_tracker_create_update_delete_persistence():
    job = requests.get(f"{BASE_URL}/api/jobs", params={"user_id": USER}).json()["jobs"][0]
    create = requests.post(f"{BASE_URL}/api/tracker", params={"user_id": USER}, json={"job_id": job["id"], "status": "saved"})
    assert create.status_code == 200
    update = requests.post(f"{BASE_URL}/api/tracker", params={"user_id": USER}, json={"job_id": job["id"], "status": "applied", "application_number": "TEST-PORTAL-1"})
    assert update.status_code == 200 and update.json()["status"] == "applied"
    tracker = requests.get(f"{BASE_URL}/api/tracker", params={"user_id": USER}).json()
    assert any(item["job_id"] == job["id"] and item["application_number"] == "TEST-PORTAL-1" for item in tracker["applied"])
    assert requests.delete(f"{BASE_URL}/api/tracker/{job['id']}", params={"user_id": USER}).status_code == 200


def test_calendar_and_daily_quiz_flow():
    calendar = requests.get(f"{BASE_URL}/api/calendar")
    assert calendar.status_code == 200 and calendar.json()["count"] > 0
    capsule = requests.get(f"{BASE_URL}/api/daily-capsule", params={"user_id": USER})
    questions = capsule.json()["capsule"]["quiz_questions"]
    quiz = requests.post(f"{BASE_URL}/api/daily-capsule/quiz-submit", params={"user_id": USER}, json={"answers": {q["id"]: q["correct_option_index"] for q in questions}})
    assert quiz.status_code == 200 and quiz.json()["score"] == len(questions)