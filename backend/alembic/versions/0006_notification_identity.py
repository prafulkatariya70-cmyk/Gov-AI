"""add government notification identity fields
Revision ID: 0006_notification_identity
Revises: 0005_notification_queue
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_notification_identity"
down_revision = "0005_notification_queue"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("jobs", sa.Column("advertisement_number", sa.String(length=50), nullable=True))
    op.add_column("jobs", sa.Column("vacancy_number", sa.String(length=50), nullable=True))
    op.create_index("ix_jobs_advertisement_number", "jobs", ["advertisement_number"])
    op.create_index("ix_jobs_vacancy_number", "jobs", ["vacancy_number"], unique=True)

def downgrade():
    op.drop_index("ix_jobs_vacancy_number", table_name="jobs")
    op.drop_index("ix_jobs_advertisement_number", table_name="jobs")
    op.drop_column("jobs", "vacancy_number")
    op.drop_column("jobs", "advertisement_number")
