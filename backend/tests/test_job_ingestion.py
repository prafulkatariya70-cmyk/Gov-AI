from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Job, JobEligibility, JobSource
from app.services.documents.parsing.notification_enhancer import NotificationParserEnhancer
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


def test_partial_reingestion_does_not_erase_verified_fields():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = Session(engine)
    try:
        parser = NotificationParser()
        service = JobIngestionService(db)

        complete = parser.parse(
            NOTIFICATION
            + """
Applications are invited from 01.09.2026 to 30.09.2026.
The salary is Rs. 44,900 - 1,42,400.
"""
        )
        job = service.ingest(
            complete,
            official_url="https://ssc.gov.in/notice/accounts-officer",
            notification_pdf_url="https://ssc.gov.in/notice/accounts-officer.pdf",
            notification_text=NOTIFICATION,
        )

        partial = parser.parse(
            """
            Staff Selection Commission (HQ)
            Recruitment to the post of Accounts Officer.
            Applications are invited for 4 posts.
            """
        )
        same = service.ingest(
            partial,
            official_url="https://ssc.gov.in/notice/accounts-officer",
            notification_pdf_url="https://ssc.gov.in/notice/accounts-officer.pdf",
            notification_text="partial-parser-pass",
        )

        assert same.id == job.id
        assert same.total_vacancies == 4
        assert same.max_age == 56
        assert same.start_date == date(2026, 9, 1)
        assert same.last_date == date(2026, 9, 30)
        assert same.salary_scale == "Rs.44,900 - 1,42,400"
    finally:
        db.close()



def test_distinct_vacancy_numbers_do_not_collide_on_shared_pdf_url():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = Session(engine)
    try:
        parser = NotificationParserEnhancer()
        service = JobIngestionService(db)
        first = parser.parse("""
        UNION PUBLIC SERVICE COMMISSION
        (Vacancy No. 26091106212) 140 posts of Assistant Public Prosecutor.
        """)
        second = parser.parse("""
        UNION PUBLIC SERVICE COMMISSION
        (Vacancy No. 26091106213) 20 posts of Assistant Director.
        """)

        first_job = service.ingest(
            first,
            official_url="https://upsc.gov.in/ad11",
            notification_pdf_url="https://upsc.gov.in/ad11.pdf",
            notification_text="(Vacancy No. 26091106212) 140 posts of Assistant Public Prosecutor.\nUNION PUBLIC SERVICE COMMISSION\n",
        )
        second_job = service.ingest(
            second,
            official_url="https://upsc.gov.in/ad11",
            notification_pdf_url="https://upsc.gov.in/ad11.pdf",
            notification_text="second block",
        )

        assert first_job.id != second_job.id
        assert first_job.vacancy_number == "26091106212"
        assert second_job.vacancy_number == "26091106213"
        assert db.query(Job).count() == 2
        assert db.query(JobSource).count() == 2
    finally:
        db.close()
