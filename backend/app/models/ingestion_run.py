from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("job_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    discovered: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    skipped: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="running",
        nullable=False,
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped["JobSource"] = relationship(
    "JobSource",
    back_populates="ingestion_runs",
)