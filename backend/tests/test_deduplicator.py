from datetime import date

from app.services.ingestion.deduplicator import (
    build_job_fingerprint,
)
from app.services.ingestion.models import DiscoveredJob


def discovered(**overrides):
    values = {
        "organization_name": "Test Commission",
        "title": "Recruitment for Assistant Engineer",
        "official_url": "https://example.gov/recruitment",
        "notification_url": "https://example.gov/notice.pdf",
        "application_end": date(2026, 10, 20),
        "source_name": "KPSC",
    }
    values.update(overrides)
    return DiscoveredJob(**values)


def test_fingerprint_prefers_external_id():
    first = discovered(
        external_id=" KPSCKA/123/2026 ",
        notification_url="https://example.gov/first.pdf",
    )
    second = discovered(
        external_id="kpscka/123/2026",
        notification_url="https://example.gov/second.pdf",
    )

    assert build_job_fingerprint(first) == build_job_fingerprint(second)


def test_fingerprint_uses_notification_url_without_external_id():
    first = discovered(
        external_id=None,
        notification_url="https://example.gov/Notice.pdf",
    )
    second = discovered(
        external_id=None,
        notification_url="https://example.gov/notice.pdf",
    )

    assert build_job_fingerprint(first) == build_job_fingerprint(second)


def test_fingerprint_is_source_scoped():
    kpsc = discovered(source_name="KPSC")
    ssc = discovered(source_name="SSC")

    assert build_job_fingerprint(kpsc) != build_job_fingerprint(ssc)


def test_fallback_fingerprint_uses_source_and_deadline():
    first = discovered(
        source_name="KPSC",
        external_id=None,
        notification_url=None,
    )
    second = discovered(
        source_name="SSC",
        external_id=None,
        notification_url=None,
    )

    assert build_job_fingerprint(first) != build_job_fingerprint(second)
