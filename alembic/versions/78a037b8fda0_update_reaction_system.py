"""update_reaction_system

Revision ID: 78a037b8fda0
Revises: 6f1cf19dfd90
Create Date: 2024-03-21 22:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '78a037b8fda0'
down_revision = '6f1cf19dfd90'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop reactions column from task_comment table if it exists
    try:
        op.drop_column('task_comment', 'reactions')
    except Exception as e:
        print(f"Warning: Could not drop reactions column: {e}")
    
    # Create indexes for faster lookups if they don't exist
    try:
        op.create_index(op.f('ix_reaction_comment_id'), 'reaction', ['comment_id'], unique=False)
    except Exception as e:
        print(f"Warning: Could not create comment_id index: {e}")
    
    try:
        op.create_index(op.f('ix_reaction_user_id'), 'reaction', ['user_id'], unique=False)
    except Exception as e:
        print(f"Warning: Could not create user_id index: {e}")

def downgrade() -> None:
    # Add back reactions column to task_comment table
    op.add_column('task_comment', sa.Column('reactions', sa.JSON(), nullable=True))
    
    # Drop reaction table and its indexes
    op.drop_index(op.f('ix_reaction_user_id'), table_name='reaction')
    op.drop_index(op.f('ix_reaction_comment_id'), table_name='reaction')
