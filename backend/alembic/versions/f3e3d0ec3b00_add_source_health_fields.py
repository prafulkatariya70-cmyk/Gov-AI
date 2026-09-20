"""add source health fields

Revision ID: f3e3d0ec3b00
Revises: 202fa8ed6f15
Create Date: 2026-08-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3e3d0ec3b00"
down_revision: Union[str, Sequence[str], None] = "202fa8ed6f15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "job_sources",
        sa.Column(
            "health_status",
            sa.String(length=50),
            nullable=False,
            server_default="healthy",
        ),
    )

    op.add_column(
        "job_sources",
        sa.Column(
            "last_error",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_sources",
        sa.Column(
            "last_success_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_job_sources_health_status",
        "job_sources",
        ["health_status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_job_sources_health_status",
        table_name="job_sources",
    )

    op.drop_column(
        "job_sources",
        "last_success_at",
    )

    op.drop_column(
        "job_sources",
        "last_error",
    )

    op.drop_column(
        "job_sources",
        "health_status",
    )