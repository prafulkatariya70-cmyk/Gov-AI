import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(300), index=True)
    slug: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    board: Mapped[str] = mapped_column(String(200), index=True)
    board_code: Mapped[str] = mapped_column(String(50), index=True)
    job_type: Mapped[str] = mapped_column(String(30), index=True)
    state: Mapped[str] = mapped_column(String(100), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    post_name: Mapped[str] = mapped_column(String(500))
    advertisement_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    vacancy_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True, index=True)
    total_vacancies: Mapped[int] = mapped_column(Integer, default=0)
    qualification_required: Mapped[str | None] = mapped_column(String(150), nullable=True)
    qualification_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exam_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    official_apply_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    official_notification_pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    official_website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_scale: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Open", index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_new_today: Mapped[bool] = mapped_column(Boolean, default=False)
    is_closing_soon: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    eligibility = relationship("JobEligibility", back_populates="job", uselist=False, cascade="all, delete-orphan")
    source = relationship("JobSource", back_populates="job", uselist=False, cascade="all, delete-orphan")
    applications = relationship("ApplicationTracker", back_populates="job")
