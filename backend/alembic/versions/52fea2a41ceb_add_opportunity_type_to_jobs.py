"""add opportunity type to jobs

Revision ID: 52fea2a41ceb
Revises: f3e3d0ec3b00
Create Date: 2026-08-26 16:27:03.276738

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "52fea2a41ceb"
down_revision: Union[str, Sequence[str], None] = "f3e3d0ec3b00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "jobs",
        sa.Column(
            "opportunity_type",
            sa.String(length=50),
            nullable=False,
            server_default="PUBLIC_RECRUITMENT",
        ),
    )

    op.create_index(
        op.f("ix_jobs_opportunity_type"),
        "jobs",
        ["opportunity_type"],
        unique=False,
    )

    # Remove the database-level default after existing rows
    # have been populated.
    op.alter_column(
        "jobs",
        "opportunity_type",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_jobs_opportunity_type"),
        table_name="jobs",
    )

    op.drop_column(
        "jobs",
        "opportunity_type",
    )