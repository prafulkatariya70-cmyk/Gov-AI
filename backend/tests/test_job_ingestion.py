from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Job, JobEligibility, JobSource
from app.services.documents.parsing.notification_parser import NotificationParser
from app.services.jobs.ingestion import JobIngestionService


NOTIFICATION = """
Staff Selection Commission (HQ)
Recruitment to the post of Accounts Officer.
Applications are invited for 4 posts.
Age limit: 21 to 56 years.
Five years' experience in Cash, Accounts and Budget work.
Candidates should have experience in government service.
The post is at Pay Level-7.
"""


def test_ingestion_persists_job_source_and_eligibility_idempotently():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = Session(engine)
    try:
        parsed = NotificationParser().parse(NOTIFICATION)
        service = JobIngestionService(db)
        job = service.ingest(
            parsed,
            official_url="https://ssc.gov.in/notice/accounts-officer",
            notification_pdf_url="https://ssc.gov.in/notice/accounts-officer.pdf",
            notification_text=NOTIFICATION,
        )
        assert job.total_vacancies == 4
        assert job.max_age == 56
        assert db.query(Job).count() == 1
        assert db.query(JobSource).count() == 1
        assert db.query(JobEligibility).count() == 1
        assert db.query(JobEligibility).one().normalized_rules

        same = service.ingest(
            parsed,
            official_url="https://ssc.gov.in/notice/accounts-officer",
            notification_pdf_url="https://ssc.gov.in/notice/accounts-officer.pdf",
            notification_text=NOTIFICATION,
        )
        assert same.id == job.id
        assert db.query(Job).count() == 1
        assert db.query(JobSource).count() == 1
        assert db.query(JobEligibility).count() == 1
    finally:
        db.close()
