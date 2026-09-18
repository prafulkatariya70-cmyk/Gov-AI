import os

# Keep the ORM metadata import test independent of a developer's local .env.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from app.core.database import Base
from app.models import ApplicationTracker, Job, JobEligibility, JobSource, User, UserProfile


def test_core_models_are_registered():
    expected = {
        "users",
        "user_profiles",
        "jobs",
        "job_eligibility",
        "job_sources",
        "application_trackers",
    }
    assert set(Base.metadata.tables) == expected


def test_core_relationships_are_declared():
    assert User.profile.property.uselist is False
    assert Job.eligibility.property.uselist is False
    assert Job.source.property.uselist is False
    assert len(User.applications.property.local_columns) == 1
    assert len(Job.applications.property.local_columns) == 1


def test_required_model_columns_exist():
    assert {"email", "is_active"}.issubset(User.__table__.columns.keys())
    assert {"user_id", "full_name", "dob", "qualification"}.issubset(UserProfile.__table__.columns.keys())
    assert {"slug", "board_code", "total_vacancies", "official_apply_url"}.issubset(Job.__table__.columns.keys())
    assert {"job_id", "normalized_rules"}.issubset(JobEligibility.__table__.columns.keys())
    assert {"job_id", "official_url", "notification_pdf_url"}.issubset(JobSource.__table__.columns.keys())
    assert {"user_id", "job_id", "status"}.issubset(ApplicationTracker.__table__.columns.keys())
