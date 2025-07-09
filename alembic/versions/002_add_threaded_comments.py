"""add threaded comments

Revision ID: 002_add_threaded_comments
Revises: 001_5_create_grants_table
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_threaded_comments'
down_revision = '001_5_create_grants_table'
branch_labels = None
depends_on = None

def upgrade():
    # Create task_comment table with all necessary columns
    op.create_table(
        'task_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('mentions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['task_comment.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reaction table
    op.create_table(
        'reaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('emoji', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['comment_id'], ['task_comment.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'comment_id', 'emoji', name='unique_user_comment_reaction')
    )

def downgrade():
    op.drop_table('reaction')
    op.drop_table('task_comment') 