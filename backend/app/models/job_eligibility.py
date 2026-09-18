import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JobEligibility(Base):
    __tablename__ = "job_eligibility"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, index=True)
    normalized_rules: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    qualification_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    special_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="eligibility")
