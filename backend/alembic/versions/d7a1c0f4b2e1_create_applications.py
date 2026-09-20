"""create applications

Revision ID: d7a1c0f4b2e1
Revises: 73ef36fd8186
"""

from alembic import op
import sqlalchemy as sa

revision = "d7a1c0f4b2e1"
down_revision = "73ef36fd8186"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("applications", sa.Column("id", sa.Integer(), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False), sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True), sa.Column("application_number", sa.String(length=150), nullable=True),
        sa.Column("roll_number", sa.String(length=150), nullable=True), sa.Column("exam_center", sa.String(length=255), nullable=True),
        sa.Column("applied_at", sa.DateTime(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_applications_id", "applications", ["id"])
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_job_id", "applications", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_applications_job_id", table_name="applications")
    op.drop_index("ix_applications_user_id", table_name="applications")
    op.drop_index("ix_applications_id", table_name="applications")
    op.drop_table("applications")
