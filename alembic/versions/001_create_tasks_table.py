"""create tasks table

Revision ID: 001_create_tasks_table
Revises: 000_create_user_table
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_create_tasks_table'
down_revision = '000_create_user_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create tasks table
    op.create_table('task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Add constraints using batch operations
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.create_check_constraint(
            'task_status_check',
            sa.text("status IN ('todo', 'in_progress', 'done', 'cancelled')")
        )
        batch_op.create_check_constraint(
            'task_priority_check',
            sa.text("priority IN ('low', 'medium', 'high', 'urgent')")
        )
        batch_op.create_foreign_key(
            'fk_task_assigned_to_id_user',
            'user',
            ['assigned_to_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_task_created_by_id_user',
            'user',
            ['created_by_id'],
            ['id']
        )

def downgrade() -> None:
    op.drop_table('task') 