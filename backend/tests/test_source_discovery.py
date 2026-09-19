from datetime import datetime, timedelta, timezone

from app.services.jobs.source_discovery import DiscoveredNotification, OfficialSourceDiscovery
from app.services.jobs.source_registry import SourceRegistryService


def test_discovery_only_returns_pdf_links():
    class FakeResponse:
        text = '''<a href="/jobs/a.pdf">Notice A</a><a href="/jobs/a.pdf">Duplicate</a><a href="/jobs/b.html">HTML</a><a href="https://example.gov/jobs/b.pdf">Notice B</a>'''
        def raise_for_status(self): pass

    import app.services.jobs.source_discovery as module
    original = module.requests.get
    module.requests.get = lambda *args, **kwargs: FakeResponse()
    try:
        results = OfficialSourceDiscovery().discover("https://example.gov/jobs")
    finally:
        module.requests.get = original
    assert [r.pdf_url for r in results] == ["https://example.gov/jobs/a.pdf", "https://example.gov/jobs/b.pdf"]


def test_due_source_logic():
    class FakeQuery:
        def filter(self, *args): return self
        def all(self): return [type("S", (), {"active": True, "last_checked_at": None, "check_interval_minutes": 60})(), type("S", (), {"active": True, "last_checked_at": datetime.now(timezone.utc), "check_interval_minutes": 60})()]
    class FakeDB:
        def query(self, *args): return FakeQuery()
    due = SourceRegistryService(FakeDB()).due_sources()
    assert len(due) == 1
