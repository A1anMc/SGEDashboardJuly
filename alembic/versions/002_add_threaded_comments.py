"""add threaded comments

Revision ID: 002_add_threaded_comments
Revises: 001_create_tasks_table
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_threaded_comments'
down_revision = '001_create_tasks_table'
branch_labels = None
depends_on = None

def upgrade():
    # Create task_comment table if it doesn't exist
    op.create_table(
        'task_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('mentions', sa.JSON(), nullable=True),
        sa.Column('reactions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['task_comment.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Add new columns to task_comment table
    op.add_column('task_comment', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column('task_comment', sa.Column('mentions', sa.JSON(), nullable=True))
    op.add_column('task_comment', sa.Column('reactions', sa.JSON(), nullable=True))
    
    # Add foreign key for parent_id
    op.create_foreign_key(
        'fk_task_comment_parent_id',
        'task_comment',
        'task_comment',
        ['parent_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Update user_id to be nullable and change ondelete to SET NULL
    op.drop_constraint('task_comment_user_id_fkey', 'task_comment', type_='foreignkey')
    op.create_foreign_key(
        'fk_task_comment_user_id',
        'task_comment',
        'user',
        ['user_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.alter_column('task_comment', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)

def downgrade():
    # Remove foreign key for parent_id
    op.drop_constraint('fk_task_comment_parent_id', 'task_comment', type_='foreignkey')
    
    # Remove new columns
    op.drop_column('task_comment', 'parent_id')
    op.drop_column('task_comment', 'mentions')
    op.drop_column('task_comment', 'reactions')
    
    # Restore user_id to be non-nullable and change ondelete back to CASCADE
    op.drop_constraint('fk_task_comment_user_id', 'task_comment', type_='foreignkey')
    op.create_foreign_key(
        'task_comment_user_id_fkey',
        'task_comment',
        'user',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.alter_column('task_comment', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)

    op.drop_table('task_comment') 