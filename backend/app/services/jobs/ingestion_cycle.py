from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.jobs.queue import NotificationQueueService
from app.services.jobs.source_registry import SourceRegistryService


@dataclass(frozen=True)
class IngestionCycleResult:
    sources_checked: int
    notifications_queued: int
    notifications_processed: int


class IngestionCycleService:
    """Run one bounded source-discovery and notification-processing cycle."""

    def __init__(self, db: Session, *, registry=None, queue=None) -> None:
        self.db = db
        self.registry = registry or SourceRegistryService(db)
        self.queue = queue or NotificationQueueService(db)

    def run(self, *, process_limit: int = 10) -> IngestionCycleResult:
        sources_checked = 0
        notifications_queued = 0

        for source in self.registry.due_sources():
            try:
                discovered = self.registry.check(source)
                notifications_queued += self.queue.enqueue_discovered(source.id, discovered)
            except Exception:
                # One unavailable official source must not stop other sources.
                continue
            sources_checked += 1

        notifications_processed = self.queue.process_due(limit=process_limit)
        return IngestionCycleResult(
            sources_checked=sources_checked,
            notifications_queued=notifications_queued,
            notifications_processed=notifications_processed,
        )
