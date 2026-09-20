"""create official job source registry

Revision ID: 9b4c2d7e1a6f
Revises: d7a1c0f4b2e1
"""

from alembic import op
import sqlalchemy as sa


revision = "9b4c2d7e1a6f"
down_revision = "d7a1c0f4b2e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_source_registry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("listing_url", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("listing_url"),
    )
    op.create_index(
        "ix_job_source_registry_id",
        "job_source_registry",
        ["id"],
    )
    op.create_index(
        "ix_job_source_registry_organization",
        "job_source_registry",
        ["organization"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_job_source_registry_organization",
        table_name="job_source_registry",
    )
    op.drop_index(
        "ix_job_source_registry_id",
        table_name="job_source_registry",
    )
    op.drop_table("job_source_registry")
