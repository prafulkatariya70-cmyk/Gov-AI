"""enforce unique application tracker per user and job

Revision ID: 0002_application_tracker_unique
Revises: 0001_initial_schema
"""
from alembic import op

revision = "0002_application_tracker_unique"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_application_tracker_user_job",
        "application_trackers",
        ["user_id", "job_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_application_tracker_user_job",
        "application_trackers",
        type_="unique",
    )
