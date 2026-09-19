"""add structured eligibility profile fields"""
from alembic import op
import sqlalchemy as sa

revision = "0003_profile_eligibility_fields"
down_revision = "0002_application_tracker_unique"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user_profiles", sa.Column("government_employee", sa.Boolean(), nullable=True))
    op.add_column("user_profiles", sa.Column("analogous_post", sa.Boolean(), nullable=True))
    op.add_column("user_profiles", sa.Column("regular_service_years", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("current_pay_level", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("parent_cadre", sa.Boolean(), nullable=True))
    op.add_column("user_profiles", sa.Column("qualifying_examination", sa.Boolean(), nullable=True))
    op.add_column("user_profiles", sa.Column("required_training", sa.Boolean(), nullable=True))
    op.add_column("user_profiles", sa.Column("relevant_experience_years", sa.Float(), nullable=True))
    op.add_column("user_profiles", sa.Column("experience_areas", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("user_profiles", "experience_areas")
    op.drop_column("user_profiles", "relevant_experience_years")
    op.drop_column("user_profiles", "required_training")
    op.drop_column("user_profiles", "qualifying_examination")
    op.drop_column("user_profiles", "parent_cadre")
    op.drop_column("user_profiles", "current_pay_level")
    op.drop_column("user_profiles", "regular_service_years")
    op.drop_column("user_profiles", "analogous_post")
    op.drop_column("user_profiles", "government_employee")
