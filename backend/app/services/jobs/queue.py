from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.notification_queue import NotificationQueueItem
from app.services.documents.processing import NotificationProcessingService

class NotificationQueueService:
    def __init__(self, db: Session, *, processor=None, max_attempts: int = 3):
        self.db=db; self.processor=processor or NotificationProcessingService(db); self.max_attempts=max_attempts
    def enqueue_discovered(self, source_registry_id, notifications) -> int:
        created=0
        for item in notifications:
            if self.db.query(NotificationQueueItem).filter(NotificationQueueItem.pdf_url==item.pdf_url).one_or_none(): continue
            self.db.add(NotificationQueueItem(source_registry_id=source_registry_id,pdf_url=item.pdf_url,source_page_url=item.source_page_url,label=item.label)); created+=1
        if created: self.db.commit()
        return created
    def process_one(self, item: NotificationQueueItem):
        item.status="PROCESSING"; item.attempts += 1; self.db.commit()
        try:
            result=self.processor.process(notification_pdf_url=item.pdf_url,official_apply_url=item.source_page_url,official_website_url=item.source_page_url)
            item.status="PROCESSED"; item.processed_at=datetime.now(timezone.utc); item.last_error=None; item.next_attempt_at=None; self.db.commit(); return result
        except Exception as exc:
            item.last_error=str(exc)[:4000]
            if item.attempts >= self.max_attempts:
                item.status="FAILED"; item.next_attempt_at=None
            else:
                item.status="PENDING"; item.next_attempt_at=datetime.now(timezone.utc)+timedelta(minutes=2**item.attempts)
            self.db.commit(); raise
    def process_due(self, limit: int = 10) -> int:
        now=datetime.now(timezone.utc)
        items=(self.db.query(NotificationQueueItem).filter(NotificationQueueItem.status=="PENDING",(NotificationQueueItem.next_attempt_at.is_(None)) | (NotificationQueueItem.next_attempt_at <= now)).order_by(NotificationQueueItem.created_at).limit(limit).all())
        processed=0
        for item in items:
            try: self.process_one(item); processed += 1
            except Exception: continue
        return processed
