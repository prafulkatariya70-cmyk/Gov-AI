from app.models.job_source import JobSource
from app.services.ingestion import runner
from app.services.ingestion.pipeline import IngestionStats


class FakeSession:
    def add(self, value):
        pass

    def flush(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass


def test_runner_degrades_source_when_eligibility_fails(monkeypatch):
    source = JobSource(
        id=1,
        name="KPSC",
        base_url="https://kpsc.kar.nic.in/",
        source_type="official_portal",
        is_active=True,
    )

    stats = IngestionStats(
        discovered=3,
        created=3,
        eligibility_failed=3,
    )

    monkeypatch.setattr(
        runner,
        "get_adapter",
        lambda source_name: object(),
    )
    monkeypatch.setattr(
        runner,
        "run_ingestion",
        lambda db, adapter: stats,
    )

    result = runner.run_source(
        db=FakeSession(),
        source=source,
    )

    assert result.status == "completed_with_errors"
    assert source.health_status == "degraded"
    assert "3 notification(s)" in source.last_error


def test_runner_counts_eligibility_failures_in_run(monkeypatch):
    source = JobSource(
        id=1,
        name="KPSC",
        base_url="https://kpsc.kar.nic.in/",
        source_type="government",
        is_active=True,
    )

    stats = IngestionStats(
        discovered=3,
        created=3,
        eligibility_failed=3,
    )

    monkeypatch.setattr(
        runner,
        "get_adapter",
        lambda source_name: object(),
    )
    monkeypatch.setattr(
        runner,
        "run_ingestion",
        lambda db, adapter: stats,
    )

    result = runner.run_source(
        db=FakeSession(),
        source=source,
    )

    assert result.status == "completed_with_errors"
    assert result.failed == 3
    assert "3 notification(s)" in result.error_message
    assert source.health_status == "degraded"


def test_runner_isolates_source_adapter_failure(monkeypatch):
    source = JobSource(
        id=2,
        name="SSC",
        base_url="https://ssc.gov.in/",
        source_type="government",
        is_active=True,
    )

    monkeypatch.setattr(
        runner,
        "get_adapter",
        lambda source_name: (_ for _ in ()).throw(
            RuntimeError("SSC temporarily unavailable")
        ),
    )

    result = runner.run_source(
        db=FakeSession(),
        source=source,
    )

    assert result.status == "failed"
    assert result.error_message == "SSC temporarily unavailable"
    assert source.health_status == "failed"
