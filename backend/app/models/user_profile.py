import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, JSON, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    domicile_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    degree_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    stream: Mapped[str | None] = mapped_column(String(150), nullable=True)
    percentage_or_cgpa: Mapped[str | None] = mapped_column(String(30), nullable=True)
    additional_certs: Mapped[str | None] = mapped_column(Text, nullable=True)
    height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Structured eligibility inputs used by the production evaluator.
    government_employee: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    analogous_post: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    regular_service_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_pay_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    parent_cadre: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    qualifying_examination: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    required_training: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    relevant_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_areas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    preferred_categories: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_states: Mapped[str | None] = mapped_column(Text, nullable=True)
    streak_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_checkin_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
