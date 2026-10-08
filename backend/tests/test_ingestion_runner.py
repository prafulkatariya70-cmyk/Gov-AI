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
