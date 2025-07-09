"""add_scraper_log_table

Revision ID: 954bc2c034cf
Revises: 004_update_grants_table
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '954bc2c034cf'
down_revision = '004_update_grants_table'
branch_labels = None
depends_on = None

def upgrade():
    # Use JSON type for SQLite
    JsonType = sa.JSON().with_variant(sqlite.JSON, "sqlite")
    
    op.create_table(
        'scraper_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(100), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('grants_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('grants_added', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('grants_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', JsonType, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scraper_logs_id', 'scraper_logs', ['id'])
    op.create_index('ix_scraper_logs_source_name', 'scraper_logs', ['source_name'])

def downgrade():
    op.drop_index('ix_scraper_logs_source_name')
    op.drop_index('ix_scraper_logs_id')
    op.drop_table('scraper_logs')
