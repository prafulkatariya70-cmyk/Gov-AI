from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.job_source_registry import JobSourceRegistry
from app.services.jobs.source_discovery import OfficialSourceDiscovery

class SourceRegistryService:
    def __init__(self, db: Session, *, discovery=None):
        self.db = db
        self.discovery = discovery or OfficialSourceDiscovery()

    def due_sources(self) -> list[JobSourceRegistry]:
        now = datetime.now(timezone.utc)
        rows = self.db.query(JobSourceRegistry).filter(JobSourceRegistry.active.is_(True)).all()
        return [r for r in rows if r.last_checked_at is None or (now - r.last_checked_at).total_seconds() >= r.check_interval_minutes * 60]

    def check(self, source: JobSourceRegistry):
        source.last_checked_at = datetime.now(timezone.utc)
        try:
            discovered = self.discovery.discover(source.listing_url)
            source.last_success_at = datetime.now(timezone.utc)
            self.db.commit()
            return discovered
        except Exception:
            self.db.commit()
            raise
