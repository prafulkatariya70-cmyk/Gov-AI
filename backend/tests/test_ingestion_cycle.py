from types import SimpleNamespace
from app.services.jobs.ingestion_cycle import IngestionCycleService


def test_cycle_discovers_enqueues_and_processes():
    source = SimpleNamespace(id="source-1")
    notification = SimpleNamespace(pdf_url="https://gov.example/a.pdf", source_page_url="https://gov.example/jobs", label="A")

    class Registry:
        def due_sources(self): return [source]
        def check(self, value): assert value is source; return [notification]

    class Queue:
        def enqueue_discovered(self, source_id, notifications):
            assert source_id == "source-1"; assert notifications == [notification]; return 1
        def process_due(self, limit): assert limit == 5; return 1

    result = IngestionCycleService(object(), registry=Registry(), queue=Queue()).run(process_limit=5)
    assert result.sources_checked == 1
    assert result.notifications_queued == 1
    assert result.notifications_processed == 1


def test_cycle_isolates_source_failure():
    sources = [SimpleNamespace(id="bad"), SimpleNamespace(id="good")]
    class Registry:
        def due_sources(self): return sources
        def check(self, source):
            if source.id == "bad": raise RuntimeError("source down")
            return []
    class Queue:
        def enqueue_discovered(self, source_id, notifications): return 0
        def process_due(self, limit): return 0
    result = IngestionCycleService(object(), registry=Registry(), queue=Queue()).run()
    assert result.sources_checked == 1
