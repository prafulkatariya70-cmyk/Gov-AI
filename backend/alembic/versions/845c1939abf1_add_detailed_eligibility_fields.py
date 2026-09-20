"""add detailed eligibility fields

Revision ID: 845c1939abf1
Revises: 52fea2a41ceb
Create Date: 2026-08-29 20:49:47.504106

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "845c1939abf1"
down_revision: Union[str, Sequence[str], None] = "52fea2a41ceb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------------------------------------------------
    # Add nullable text fields
    # ------------------------------------------------------------

    op.add_column(
        "job_eligibility",
        sa.Column(
            "experience_requirement",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_eligibility",
        sa.Column(
            "service_requirement",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_eligibility",
        sa.Column(
            "department_requirement",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_eligibility",
        sa.Column(
            "qualification_text",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_eligibility",
        sa.Column(
            "special_requirements",
            sa.Text(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------
    # Government service requirement
    #
    # Existing records must receive False.
    # ------------------------------------------------------------

    op.add_column(
        "job_eligibility",
        sa.Column(
            "requires_government_service",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE job_eligibility
        SET requires_government_service = FALSE
        WHERE requires_government_service IS NULL
        """
    )

    op.alter_column(
        "job_eligibility",
        "requires_government_service",
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "job_eligibility",
        "special_requirements",
    )

    op.drop_column(
        "job_eligibility",
        "qualification_text",
    )

    op.drop_column(
        "job_eligibility",
        "department_requirement",
    )

    op.drop_column(
        "job_eligibility",
        "service_requirement",
    )

    op.drop_column(
        "job_eligibility",
        "requires_government_service",
    )

    op.drop_column(
        "job_eligibility",
        "experience_requirement",
    )