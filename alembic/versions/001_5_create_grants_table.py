"""create grants table

Revision ID: 001_5_create_grants_table
Revises: 001_2_create_project_table
Create Date: 2024-03-21 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_5_create_grants_table'
down_revision = '001_2_create_project_table'
branch_labels = None
depends_on = None

def upgrade():
    # Create grants table
    op.create_table(
        'grants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_grants_source'), 'grants', ['source'], unique=False)
    op.create_index(op.f('ix_grants_status'), 'grants', ['status'], unique=False)
    op.create_index(op.f('ix_grants_deadline'), 'grants', ['deadline'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_grants_deadline'), table_name='grants')
    op.drop_index(op.f('ix_grants_status'), table_name='grants')
    op.drop_index(op.f('ix_grants_source'), table_name='grants')
    op.drop_table('grants')