from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    base_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    check_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    health_status: Mapped[str] = mapped_column(
        String(50),
        default="healthy",
        nullable=False,
        index=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(
        "IngestionRun",
        back_populates="source",
        cascade="all, delete-orphan",
    )