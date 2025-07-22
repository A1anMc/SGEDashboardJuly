"""Add user profiles table

Revision ID: add_user_profiles_table
Revises: 27eb933
Create Date: 2025-01-22 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_profiles_table'
down_revision = '27eb933'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_name', sa.String(length=255), nullable=False),
        sa.Column('organization_type', sa.String(length=100), nullable=False),
        sa.Column('industry_focus', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('preferred_funding_range_min', sa.Integer(), nullable=True),
        sa.Column('preferred_funding_range_max', sa.Integer(), nullable=True),
        sa.Column('preferred_industries', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_locations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_org_types', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('max_deadline_days', sa.Integer(), nullable=True),
        sa.Column('min_grant_amount', sa.Integer(), nullable=True),
        sa.Column('max_grant_amount', sa.Integer(), nullable=True),
        sa.Column('email_notifications', sa.String(length=50), nullable=True),
        sa.Column('deadline_alerts', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_profiles_id'), table_name='user_profiles')
    op.drop_table('user_profiles') 