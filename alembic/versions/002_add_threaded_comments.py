"""add threaded comments

Revision ID: 002_add_threaded_comments
Revises: 001_7_create_task_related_tables
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_threaded_comments'
down_revision = '001_7_create_task_related_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to task_comment table for threaded comments
    op.add_column('task_comment', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column('task_comment', sa.Column('mentions', sa.JSON(), nullable=True))
    op.add_column('task_comment', sa.Column('reactions', sa.JSON(), nullable=True))

def downgrade():
    # Remove new columns
    op.drop_column('task_comment', 'parent_id')
    op.drop_column('task_comment', 'mentions')
    op.drop_column('task_comment', 'reactions') 