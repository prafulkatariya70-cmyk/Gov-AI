from datetime import date, timedelta
from types import SimpleNamespace

from app.models.job import Job
from app.services.documents.parsing.notification_parser import NotificationParser
from app.services.ingestion import runner
from app.services.ingestion.pipeline import IngestionStats
from app.services.job_lifecycle import lifecycle_metadata, lifecycle_status


def job(**overrides):
    values = {
        "organization_name": "Test Commission",
        "title": "Test Job",
        "official_url": "https://example.gov/job",
        "status": "active",
    }
    values.update(overrides)
    return Job(**values)


def test_current_upcoming_expired_closed_unknown_and_deadline_boundary():
    today = date(2026, 9, 19)
    assert lifecycle_status(job(application_start=today - timedelta(days=1), application_end=today), today) == "CURRENT"
    assert lifecycle_status(job(application_start=today + timedelta(days=1), application_end=today + timedelta(days=10)), today) == "UPCOMING"
    assert lifecycle_status(job(application_end=today - timedelta(days=1)), today) == "EXPIRED"
    assert lifecycle_status(job(status="closed", application_end=today + timedelta(days=1)), today) == "CLOSED"
    assert lifecycle_status(job(application_end=None), today) == "UNKNOWN"
    assert lifecycle_metadata(job(application_end=today + timedelta(days=7)), today)["is_closing_soon"] is True


def test_parser_supports_written_online_window_dates():
    parsed = NotificationParser().parse(
        "The online application window opens on 20 September 2026 and closes on 20 October 2026."
    )
    assert parsed.application_start.value == date(2026, 9, 20)
    assert parsed.application_end.value == date(2026, 10, 20)


def test_successful_empty_source_check_remains_healthy(monkeypatch):
    class FakeDb:
        def add(self, _value): pass
        def flush(self): pass
        def commit(self): pass
        def rollback(self): pass

    source = SimpleNamespace(id=99, name="TEST", last_checked_at=None, health_status="healthy", last_error="old error", last_success_at=None)
    monkeypatch.setattr(runner, "get_adapter", lambda _name: object())
    monkeypatch.setattr(runner, "run_ingestion", lambda **_kwargs: IngestionStats(discovered=0))

    result = runner.run_source(FakeDb(), source)
    assert result.status == "success"
    assert source.health_status == "healthy"
    assert source.last_error is None
    assert source.last_success_at is not None
