"""create project table

Revision ID: 001_2_create_project_table
Revises: 001_create_tasks_table
Create Date: 2024-03-21 09:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_2_create_project_table'
down_revision = '001_create_tasks_table'
branch_labels = None
depends_on = None

def upgrade():
    # Create project table
    op.create_table(
        'project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('budget', sa.Numeric(10, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_project_name'), 'project', ['name'], unique=True)
    op.create_index(op.f('ix_project_status'), 'project', ['status'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_project_status'), table_name='project')
    op.drop_index(op.f('ix_project_name'), table_name='project')
    op.drop_table('project')