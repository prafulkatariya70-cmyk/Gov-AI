import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ApplicationTracker(Base):
    __tablename__ = "application_trackers"

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_application_tracker_user_job"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="saved", index=True)
    application_number: Mapped[str | None] = mapped_column(String(150), nullable=True)
    roll_number: Mapped[str | None] = mapped_column(String(150), nullable=True)
    exam_center: Mapped[str | None] = mapped_column(String(300), nullable=True)
    applied_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    exam_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
