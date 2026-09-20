from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class JobEligibility(Base):
    __tablename__ = "job_eligibility"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    # ================================================================
    # AGE
    # ================================================================

    minimum_age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    maximum_age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ================================================================
    # EDUCATION
    # ================================================================

    education_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    degree: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    branch: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # ================================================================
    # EXPERIENCE
    # ================================================================

    minimum_experience_years: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    experience_requirement: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ================================================================
    # GOVERNMENT / SERVICE REQUIREMENTS
    # ================================================================

    requires_government_service: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    service_requirement: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    department_requirement: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ================================================================
    # QUALIFICATION
    # ================================================================

    qualification_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ================================================================
    # LOCATION / CATEGORY
    # ================================================================

    eligible_states: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    eligible_categories: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ================================================================
    # SPECIAL REQUIREMENTS
    # ================================================================

    special_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ================================================================
    # NORMALIZED ELIGIBILITY RULES
    # ================================================================
    #
    # Stores structured eligibility rules extracted from the
    # notification parser.
    #
    # Example:
    #
    # {
    #     "rules": [
    #         {
    #             "rule_type": "AGE",
    #             "minimum": 18,
    #             "maximum": 30
    #         },
    #         {
    #             "rule_type": "GOVERNMENT_SERVICE",
    #             "required": true
    #         }
    #     ]
    # }
    #
    # JSON is intentionally nullable because older jobs may not yet
    # have normalized rules generated.
    #

    normalized_rules: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ================================================================
    # CREATED / UPDATED
    # ================================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # ================================================================
    # RELATIONSHIP
    # ================================================================

    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="eligibility",
    )