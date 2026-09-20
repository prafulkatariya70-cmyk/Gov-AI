from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JobSourceRegistry(Base):
    __tablename__ = "job_source_registry"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    organization: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    listing_url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
