from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    organization_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    official_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    notification_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    application_start: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    application_end: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
        index=True,
    )

    opportunity_type: Mapped[str] = mapped_column(
        String(50),
        default="PUBLIC_RECRUITMENT",
        nullable=False,
        index=True,
    )

    source_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    eligibility: Mapped["JobEligibility | None"] = relationship(
        "JobEligibility",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )