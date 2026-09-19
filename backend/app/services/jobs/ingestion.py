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
from app.services.jobs.status import derive_job_status

class JobIngestionService:
    def __init__(self, db: Session) -> None:
        self.db=db; self.eligibility=EligibilityPersistence(db)

    def ingest(self, parsed: ParsedNotification, *, official_url: str, notification_pdf_url: str|None=None, official_website_url: str|None=None, official_apply_url: str|None=None, notification_text: str="") -> Job:
        if not official_url or urlparse(official_url).scheme not in {"http","https"}: raise ValueError("A valid official source URL is required.")
        if not parsed.title.value: raise ValueError("Notification title is required before ingestion.")
        content_hash=hashlib.sha256(notification_text.encode("utf-8")).hexdigest() if notification_text else None
        source=self._find_source(official_url, notification_pdf_url, content_hash, self._field_value(parsed, "vacancy_number"))
        job=self._find_job(source, parsed)
        if job is None:
            title=str(parsed.title.value).strip(); board=str(parsed.organization_name.value or "Government Recruitment").strip()
            job=Job(title=title,slug=self._slug(title,board,content_hash),board=board,board_code=self._board_code(board),job_type=str(parsed.opportunity_type.value or "RECRUITMENT").strip(),state="All India",category="Government Jobs",post_name=title,advertisement_number=self._field_value(parsed,"advertisement_number"),vacancy_number=self._field_value(parsed,"vacancy_number"),total_vacancies=self._int_value(parsed.vacancy_count.value) or 0,qualification_required=str(parsed.degree.value) if parsed.degree.value else None,qualification_details=self._field_text(parsed,"qualification_text"),min_age=self._int_value(parsed.minimum_age.value),max_age=self._int_value(parsed.maximum_age.value),start_date=self._date_value(parsed.application_start.value),last_date=self._date_value(parsed.application_end.value),salary_scale=self._field_text(parsed,"salary_text"),official_apply_url=official_apply_url,official_notification_pdf_url=notification_pdf_url,official_website_url=official_website_url or official_url,status="NO_DEADLINE",is_new_today=False)
            self.db.add(job); self.db.flush()
        else: self._update_job(job,parsed,official_url,notification_pdf_url,official_website_url,official_apply_url)
        self._refresh_status(job)
        self.eligibility.persist(job,parsed); self.db.flush()
        if source is None: source=JobSource(job_id=job.id); self.db.add(source)
        source.organization=str(parsed.organization_name.value) if parsed.organization_name.value else None
        source.official_url=official_url; source.notification_pdf_url=notification_pdf_url; source.source_type="official"; source.last_checked_at=datetime.now(timezone.utc); source.last_processed_at=datetime.now(timezone.utc); source.content_hash=content_hash
        self.db.commit(); self.db.refresh(job); return job

    def _find_source(self, official_url, pdf_url, content_hash, vacancy_number=None):
        # A content hash is block-specific, so it is the safest idempotency key
        # when several posts share one advertisement PDF.
        if content_hash:
            source = self.db.query(JobSource).filter(JobSource.content_hash == content_hash).one_or_none()
            if source is not None:
                return source

        # Multi-post advertisements can share official/PDF URLs. Resolve the
        # source through the post's explicit vacancy number before URL matching.
        if vacancy_number:
            job = self.db.query(Job).filter(Job.vacancy_number == vacancy_number).one_or_none()
            if job is not None:
                source = self.db.query(JobSource).filter(JobSource.job_id == job.id).one_or_none()
                if source is not None:
                    return source

        if official_url:
            source = self.db.query(JobSource).filter(JobSource.official_url == official_url).one_or_none()
            if source is not None:
                return source
        if pdf_url:
            source = self.db.query(JobSource).filter(JobSource.notification_pdf_url == pdf_url).one_or_none()
            if source is not None:
                return source
        return None

    def _find_job(self,source,parsed):
        if source is not None:
            return self.db.get(Job,source.job_id)
        vacancy_number = self._field_value(parsed, "vacancy_number")
        if vacancy_number:
            job = self.db.query(Job).filter(Job.vacancy_number == vacancy_number).one_or_none()
            if job is not None:
                return job
        title=str(parsed.title.value or "").strip()
        board=str(parsed.organization_name.value or "").strip()
        return self.db.query(Job).filter(Job.title==title,Job.board==board).one_or_none()

    def _update_job(self,job,parsed,official_url,pdf_url,website_url,apply_url):
        vacancy_count = self._int_value(parsed.vacancy_count.value)
        min_age = self._int_value(parsed.minimum_age.value)
        max_age = self._int_value(parsed.maximum_age.value)
        qualification_required = str(parsed.degree.value).strip() if parsed.degree.value else None
        qualification_details = self._field_text(parsed,"qualification_text")
        start_date = self._date_value(parsed.application_start.value)
        last_date = self._date_value(parsed.application_end.value)
        salary_scale = self._field_text(parsed,"salary_text")

        # Parser passes can be partial. Never erase a previously verified value
        # merely because a later extraction did not recover that field.
        advertisement_number = self._field_value(parsed, "advertisement_number")
        vacancy_number = self._field_value(parsed, "vacancy_number")
        if advertisement_number:
            job.advertisement_number = advertisement_number
        if vacancy_number:
            job.vacancy_number = vacancy_number
        if vacancy_count is not None:
            job.total_vacancies = vacancy_count
        if min_age is not None:
            job.min_age = min_age
        if max_age is not None:
            job.max_age = max_age
        if qualification_required:
            job.qualification_required = qualification_required
        if qualification_details:
            job.qualification_details = qualification_details
        if start_date is not None:
            job.start_date = start_date
        if last_date is not None:
            job.last_date = last_date
        if salary_scale:
            job.salary_scale = salary_scale
        if pdf_url:
            job.official_notification_pdf_url = pdf_url
        if website_url:
            job.official_website_url = website_url
        if apply_url:
            job.official_apply_url = apply_url

    @staticmethod
    def _refresh_status(job: Job) -> None:
        lifecycle = derive_job_status(
            start_date=job.start_date,
            last_date=job.last_date,
            notification_date=job.notification_date,
        )
        job.status = lifecycle.status
        job.is_closing_soon = lifecycle.is_closing_soon
        job.is_new_today = lifecycle.is_new_today

    @staticmethod
    def _field_value(parsed, field_name):
        field = getattr(parsed, field_name, None)
        if field is None:
            return None
        value = field.value
        return str(value).strip() if value is not None and str(value).strip() else None

    @staticmethod
    def _field_text(parsed,field_name):
        value=getattr(parsed,field_name).value; return str(value).strip() if value is not None else None
    @staticmethod
    def _int_value(value):
        try: return int(value) if value is not None else None
        except (TypeError,ValueError): return None
    @staticmethod
    def _date_value(value): return value if isinstance(value,date) else None
    @staticmethod
    def _board_code(value):
        words=re.findall(r"[A-Za-z]+",str(value or "Government")); return "".join(w[0] for w in words).upper()[:12] or "GOV"
    @staticmethod
    def _slug(title,organization,content_hash):
        base=re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-") or "government-job"; org=re.sub(r"[^a-z0-9]+","-",str(organization or "gov").lower()).strip("-"); fingerprint=(content_hash or hashlib.sha256(f"{title}|{organization}".encode()).hexdigest())[:10]; return f"{base}-{org}-{fingerprint}"[:290].rstrip("-")
