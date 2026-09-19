from datetime import datetime, timezone
from types import SimpleNamespace
from app.services.jobs.queue import NotificationQueueService
from app.models.notification_queue import NotificationQueueItem

def test_enqueue_is_idempotent():
    class Q:
        def __init__(self): self.items=[]
        def filter(self,*a,**k): return self
        def one_or_none(self): return self.items[0] if self.items else None
    class DB:
        def __init__(self): self.q=Q(); self.added=[]
        def query(self,*a): return self.q
        def add(self,x): self.added.append(x); self.q.items.append(x)
        def commit(self): pass
    db=DB(); svc=NotificationQueueService(db,processor=SimpleNamespace())
    n=SimpleNamespace(pdf_url="https://gov.example/a.pdf",source_page_url="https://gov.example/jobs",label="A")
    assert svc.enqueue_discovered("source",[n]) == 1
    assert svc.enqueue_discovered("source",[n]) == 0

def test_failed_item_retries_then_fails():
    class DB:
        def commit(self): pass
    item=NotificationQueueItem(source_registry_id="00000000-0000-0000-0000-000000000001",pdf_url="https://gov.example/a.pdf",source_page_url="https://gov.example/jobs",label="A")
    class Processor:
        def process(self,**kwargs): raise ValueError("bad pdf")
    svc=NotificationQueueService(DB(),processor=Processor(),max_attempts=1)
    try: svc.process_one(item)
    except ValueError: pass
    assert item.status == "FAILED"
    assert item.attempts == 1
    assert item.last_error == "bad pdf"
