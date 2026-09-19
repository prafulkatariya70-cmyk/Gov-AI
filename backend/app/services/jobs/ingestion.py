from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_source import JobSource
from app.services.documents.parsing.notification_parser import ParsedNotification
from app.services.eligibility.persistence import EligibilityPersistence


class JobIngestionService:
    """Persist one parsed official notification as an idempotent job record.

    Document retrieval is intentionally separate: callers provide already extracted
    notification text and the official source URLs. This keeps ingestion deterministic
    and prevents network/OCR work from leaking into request-time APIs.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.eligibility = EligibilityPersistence(db)

    def ingest(
        self,
        parsed: ParsedNotification,
        *,
        official_url: str,
        notification_pdf_url: str | None = None,
        official_website_url: str | None = None,
        notification_text: str = "",
    ) -> Job:
        if not official_url or not urlparse(official_url).scheme:
            raise ValueError("A valid official source URL is required.")
        if not parsed.title.value:
            raise ValueError("Notification title is required before ingestion.")

        content_hash = hashlib.sha256(notification_text.encode("utf-8")).hexdigest() if notification_text else None
        source = self._find_source(official_url, notification_pdf_url, content_hash)
        job = self._find_job(source, parsed)

        if job is None:
            title = str(parsed.title.value).strip()
            job = Job(
                title=title,
                slug=self._slug(title, parsed.organization_name.value),
                board=str(parsed.organization_name.value or "Government Recruitment").strip(),
                board_code=self._board_code(parsed.organization_name.value),
                job_type=str(parsed.opportunity_type.value or "RECRUITMENT").strip(),
                state="All India",
                category="Government Jobs",
                post_name=title,
                total_vacancies=int(parsed.vacancy_count.value or 0),
                qualification_required=str(parsed.degree.value) if parsed.degree.value else None,
                qualification_details=self._field_text(parsed, "qualification_text"),
                min_age=self._int_value(parsed.minimum_age.value),
                max_age=self._int_value(parsed.maximum_age.value),
                start_date=self._date_value(parsed.application_start.value),
                last_date=self._date_value(parsed.application_end.value),
                salary_scale=self._field_text(parsed, "salary_text"),
                official_apply_url=official_url,
                official_notification_pdf_url=notification_pdf_url,
                official_website_url=official_website_url or official_url,
                status="Open",
                is_new_today=True,
            )
            self.db.add(job)
            self.db.flush()
        else:
            self._update_job(job, parsed, official_url, notification_pdf_url, official_website_url)

        eligibility = self.eligibility.persist(job, parsed)
        self.db.flush()

        if source is None:
            source = JobSource(job_id=job.id)
            self.db.add(source)
        source.organization = str(parsed.organization_name.value) if parsed.organization_name.value else None
        source.official_url = official_url
        source.notification_pdf_url = notification_pdf_url
        source.source_type = "official"
        source.last_checked_at = datetime.now(timezone.utc)
        source.last_processed_at = datetime.now(timezone.utc)
        source.content_hash = content_hash
        self.db.commit()
        self.db.refresh(job)
        return job

    def _find_source(self, official_url: str, pdf_url: str | None, content_hash: str | None) -> JobSource | None:
        query = self.db.query(JobSource).filter(JobSource.official_url == official_url)
        if pdf_url:
            query = query.filter(JobSource.notification_pdf_url == pdf_url)
        source = query.one_or_none()
        if source is not None:
            return source
        if content_hash:
            return self.db.query(JobSource).filter(JobSource.content_hash == content_hash).one_or_none()
        return None

    def _find_job(self, source: JobSource | None, parsed: ParsedNotification) -> Job | None:
        if source is not None:
            return self.db.get(Job, source.job_id)
        title = str(parsed.title.value or "").strip()
        return self.db.query(Job).filter(Job.title == title, Job.board == str(parsed.organization_name.value or "").strip()).one_or_none()

    def _update_job(self, job: Job, parsed: ParsedNotification, official_url: str, pdf_url: str | None, website_url: str | None) -> None:
        job.total_vacancies = self._int_value(parsed.vacancy_count.value) or job.total_vacancies
        job.min_age = self._int_value(parsed.minimum_age.value)
        job.max_age = self._int_value(parsed.maximum_age.value)
        job.qualification_required = str(parsed.degree.value) if parsed.degree.value else job.qualification_required
        job.qualification_details = self._field_text(parsed, "qualification_text")
        job.start_date = self._date_value(parsed.application_start.value)
        job.last_date = self._date_value(parsed.application_end.value)
        job.salary_scale = self._field_text(parsed, "salary_text")
        job.official_apply_url = official_url
        job.official_notification_pdf_url = pdf_url
        job.official_website_url = website_url or job.official_website_url

    @staticmethod
    def _field_text(parsed: ParsedNotification, field_name: str) -> str | None:
        value = getattr(parsed, field_name).value
        return str(value).strip() if value is not None else None

    @staticmethod
    def _int_value(value) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _date_value(value) -> date | None:
        return value if isinstance(value, date) else None

    @staticmethod
    def _board_code(value) -> str:
        words = re.findall(r"[A-Za-z]+", str(value or "Government"))
        return "".join(word[0] for word in words).upper()[:12] or "GOV"

    @staticmethod
    def _slug(title: str, organization) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "government-job"
        org = re.sub(r"[^a-z0-9]+", "-", str(organization or "gov").lower()).strip("-")
        return f"{base}-{org}"[:290].rstrip("-")
