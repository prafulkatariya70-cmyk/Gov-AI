from types import SimpleNamespace

from app.services.ingestion import pipeline


def test_failed_notification_fetch_is_not_parsed(monkeypatch):
    class FakeFetcher:
        def fetch(self, url):
            return SimpleNamespace(
                success=False,
                content=None,
            )

    class UnexpectedExtractor:
        def __init__(self):
            raise AssertionError(
                "PDF extraction must not run after fetch failure"
            )

    monkeypatch.setattr(
        pipeline,
        "DocumentFetcher",
        FakeFetcher,
    )
    monkeypatch.setattr(
        pipeline,
        "PDFTextExtractor",
        UnexpectedExtractor,
    )

    job = SimpleNamespace(
        notification_url="https://example.gov/notice.pdf",
        eligibility=None,
    )

    result = pipeline._parse_and_save_eligibility(
        db=None,
        job=job,
    )

    assert result == "failed"


def test_missing_notification_content_is_not_parsed(monkeypatch):
    class FakeFetcher:
        def fetch(self, url):
            return SimpleNamespace(
                success=True,
                content=None,
            )

    class UnexpectedExtractor:
        def __init__(self):
            raise AssertionError(
                "PDF extraction must not run without document content"
            )

    monkeypatch.setattr(
        pipeline,
        "DocumentFetcher",
        FakeFetcher,
    )
    monkeypatch.setattr(
        pipeline,
        "PDFTextExtractor",
        UnexpectedExtractor,
    )

    job = SimpleNamespace(
        notification_url="https://example.gov/notice.pdf",
        eligibility=None,
    )

    result = pipeline._parse_and_save_eligibility(
        db=None,
        job=job,
    )

    assert result == "failed"
