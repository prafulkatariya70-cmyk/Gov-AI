"""create official job source registry

Revision ID: 0004_source_registry
Revises: 0003_profile_eligibility_fields
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_source_registry"
down_revision = "0003_profile_eligibility_fields"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "job_source_registry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("listing_url", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("check_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("etag", sa.String(length=300), nullable=True),
        sa.Column("last_modified", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("listing_url"),
    )
    op.create_index("ix_job_source_registry_organization", "job_source_registry", ["organization"])
    op.create_index("ix_job_source_registry_active", "job_source_registry", ["active"])

def downgrade():
    op.drop_index("ix_job_source_registry_active", table_name="job_source_registry")
    op.drop_index("ix_job_source_registry_organization", table_name="job_source_registry")
    op.drop_table("job_source_registry")
