"""update grants table

Revision ID: 004_update_grants_table
Revises: 003_add_tag_system
Create Date: 2024-03-21 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_update_grants_table'
down_revision = '003_add_tag_system'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    with op.batch_alter_table('grants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source_url', sa.String(length=1000), nullable=True))
        batch_op.add_column(sa.Column('application_url', sa.String(length=1000), nullable=True))
        batch_op.add_column(sa.Column('contact_email', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('min_amount', sa.Numeric(10, 2), nullable=True))
        batch_op.add_column(sa.Column('max_amount', sa.Numeric(10, 2), nullable=True))
        batch_op.add_column(sa.Column('open_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('industry_focus', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('location_eligibility', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('org_type_eligible', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('funding_purpose', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('audience_tags', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    # Remove columns
    with op.batch_alter_table('grants', schema=None) as batch_op:
        batch_op.drop_column('notes')
        batch_op.drop_column('audience_tags')
        batch_op.drop_column('funding_purpose')
        batch_op.drop_column('org_type_eligible')
        batch_op.drop_column('location_eligibility')
        batch_op.drop_column('industry_focus')
        batch_op.drop_column('open_date')
        batch_op.drop_column('max_amount')
        batch_op.drop_column('min_amount')
        batch_op.drop_column('contact_email')
        batch_op.drop_column('application_url')
        batch_op.drop_column('source_url') 