from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Job, JobEligibility
from app.services.documents.parsing.notification_parser import NotificationParser
from app.services.documents.parsing.rules.normalizer import EligibilityNormalizer
from app.services.eligibility.persistence import EligibilityPersistence


NOTIFICATION = """
Staff Selection Commission (HQ)
Recruitment to the post of Accounts Officer on deputation.
Applications are invited for 4 posts.
Age limit: 21 to 56 years.
Possessing the following qualifications and experience:
(i) A pass in the Subordinate Accounts Services or equivalent examination
conducted by the Accounts Departments of the Central Government; or
(ii) Successful completion of training in the Cash and Accounts Work in the ISTM or equivalent;
and (iii) Five years' experience in Cash, Accounts and Budget work.
Candidates should have experience in government service.
The post is at Pay Level-7.
"""


def make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def make_job() -> Job:
    return Job(
        title="Accounts Officer",
        slug="accounts-officer-test",
        board="Staff Selection Commission",
        board_code="SSC",
        job_type="DEPUTATION",
        state="Central",
        category="Accounts",
        post_name="Accounts Officer",
        total_vacancies=4,
    )


def test_persistence_creates_and_round_trips_normalized_rules():
    db = make_session()
    try:
        job = make_job()
        db.add(job)
        db.flush()

        parsed = NotificationParser().parse(NOTIFICATION)
        normalized = EligibilityNormalizer().normalize(parsed)
        persisted = EligibilityPersistence(db).persist(job, parsed, normalized)
        db.commit()

        loaded = db.query(JobEligibility).filter_by(job_id=job.id).one()

        assert persisted.id == loaded.id
        assert loaded.normalized_rules is not None
        assert loaded.normalized_rules["age_rules"][0]["rule_type"] == "MINIMUM_AGE"
        assert loaded.normalized_rules["age_rules"][1]["rule_type"] == "MAXIMUM_AGE"
        assert loaded.qualification_text == parsed.qualification_text.value
        assert loaded.service_requirement == parsed.service_requirement.value
        assert loaded.special_requirements == parsed.special_requirements.value
    finally:
        db.close()


def test_persistence_updates_existing_record_instead_of_duplicating():
    db = make_session()
    try:
        job = make_job()
        db.add(job)
        db.flush()

        parsed = NotificationParser().parse(NOTIFICATION)
        persistence = EligibilityPersistence(db)

        first = persistence.persist(job, parsed)
        db.commit()

        second = persistence.persist(job, parsed)
        db.commit()

        assert first.id == second.id
        assert db.query(JobEligibility).filter_by(job_id=job.id).count() == 1
    finally:
        db.close()
