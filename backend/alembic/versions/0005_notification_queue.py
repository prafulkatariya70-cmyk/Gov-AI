"""create notification processing queue
Revision ID: 0005_notification_queue
Revises: 0004_source_registry
"""
from alembic import op
import sqlalchemy as sa
revision="0005_notification_queue"; down_revision="0004_source_registry"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("notification_queue",sa.Column("id",sa.Uuid(),nullable=False),sa.Column("source_registry_id",sa.Uuid(),nullable=False),sa.Column("pdf_url",sa.Text(),nullable=False),sa.Column("source_page_url",sa.Text(),nullable=False),sa.Column("label",sa.String(500),nullable=False),sa.Column("status",sa.String(30),nullable=False),sa.Column("attempts",sa.Integer(),nullable=False),sa.Column("next_attempt_at",sa.DateTime(timezone=True),nullable=True),sa.Column("last_error",sa.Text(),nullable=True),sa.Column("processed_at",sa.DateTime(timezone=True),nullable=True),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),sa.ForeignKeyConstraint(["source_registry_id"],["job_source_registry.id"],ondelete="CASCADE"),sa.PrimaryKeyConstraint("id"),sa.UniqueConstraint("pdf_url"))
 op.create_index("ix_notification_queue_source_registry_id","notification_queue",["source_registry_id"]); op.create_index("ix_notification_queue_status","notification_queue",["status"]); op.create_index("ix_notification_queue_next_attempt_at","notification_queue",["next_attempt_at"])
def downgrade():
 op.drop_index("ix_notification_queue_next_attempt_at",table_name="notification_queue"); op.drop_index("ix_notification_queue_status",table_name="notification_queue"); op.drop_index("ix_notification_queue_source_registry_id",table_name="notification_queue"); op.drop_table("notification_queue")
