from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.documents.fetcher import DocumentFetcher
from app.services.documents.pdf_extractor import PDFTextExtractor
from app.services.documents.parsing.notification_parser import NotificationParser
from app.services.jobs.ingestion import JobIngestionService


@dataclass(frozen=True)
class NotificationProcessingResult:
    job_id: object
    content_hash: str
    extraction_method: str
    page_count: int
    extracted_text_length: int


class NotificationProcessingService:
    """Run fetch → PDF extraction → parser → PostgreSQL ingestion."""

    def __init__(self, db: Session, *, fetcher=None, extractor=None, parser=None) -> None:
        self.fetcher = fetcher or DocumentFetcher()
        self.extractor = extractor or PDFTextExtractor()
        self.parser = parser or NotificationParser()
        self.ingestion = JobIngestionService(db)

    def process(
        self,
        *,
        notification_pdf_url: str,
        official_apply_url: str,
        official_website_url: str | None = None,
    ) -> NotificationProcessingResult:
        document = self.fetcher.fetch(notification_pdf_url)
        extracted = self.extractor.extract(document.content)
        if not extracted.text.strip():
            raise ValueError("Notification PDF produced no extractable text.")

        parsed = self.parser.parse(extracted.text)
        job = self.ingestion.ingest(
            parsed,
            official_url=official_apply_url,
            notification_pdf_url=notification_pdf_url,
            official_website_url=official_website_url,
            notification_text=extracted.text,
        )
        return NotificationProcessingResult(
            job_id=job.id,
            content_hash=document.content_hash,
            extraction_method=extracted.method,
            page_count=extracted.page_count,
            extracted_text_length=len(extracted.text),
        )
