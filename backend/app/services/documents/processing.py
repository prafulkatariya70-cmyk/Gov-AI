from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.documents.fetcher import DocumentFetcher
from app.services.documents.pdf_extractor import PDFTextExtractor
from app.services.documents.parsing.notification_enhancer import NotificationParserEnhancer
from app.services.documents.parsing.notification_post_splitter import NotificationPostSplitter
from app.services.jobs.ingestion import JobIngestionService


@dataclass(frozen=True)
class NotificationProcessingResult:
    job_id: object
    content_hash: str
    extraction_method: str
    page_count: int
    extracted_text_length: int
    jobs_created_or_updated: int = 1


class NotificationProcessingService:
    """Run fetch → PDF extraction → split → parse → PostgreSQL ingestion."""

    def __init__(self, db: Session, *, fetcher=None, extractor=None, parser=None, splitter=None) -> None:
        self.fetcher = fetcher or DocumentFetcher()
        self.extractor = extractor or PDFTextExtractor()
        self.parser = parser or NotificationParserEnhancer()
        self.splitter = splitter or NotificationPostSplitter()
        self.ingestion = JobIngestionService(db)

    def process(
        self,
        *,
        notification_pdf_url: str,
        official_source_url: str,
        official_website_url: str | None = None,
        official_apply_url: str | None = None,
    ) -> NotificationProcessingResult:
        document = self.fetcher.fetch(notification_pdf_url)
        extracted = self.extractor.extract(document.content)
        if not extracted.text.strip():
            raise ValueError("Notification PDF produced no extractable text.")

        blocks = self.splitter.split(extracted.text)
        if not blocks:
            raise ValueError("Notification PDF produced no notification blocks.")

        jobs = []
        for block in blocks:
            parsed = self.parser.parse(block.text)
            if not parsed.title.value:
                raise ValueError(
                    f"Could not identify a post title for vacancy {block.vacancy_number or 'unknown'}."
                )
            jobs.append(
                self.ingestion.ingest(
                    parsed,
                    official_url=official_source_url,
                    official_apply_url=official_apply_url,
                    notification_pdf_url=notification_pdf_url,
                    official_website_url=official_website_url,
                    notification_text=block.text,
                )
            )

        return NotificationProcessingResult(
            job_id=jobs[0].id,
            content_hash=document.content_hash,
            extraction_method=extracted.method,
            page_count=extracted.page_count,
            extracted_text_length=len(extracted.text),
            jobs_created_or_updated=len(jobs),
        )
