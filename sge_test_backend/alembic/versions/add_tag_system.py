"""add tag system

Revision ID: add_tag_system
Revises: 2044ada86cad
Create Date: 2024-03-21 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_tag_system'
down_revision = '2044ada86cad'
branch_labels = None
depends_on = None

def upgrade():
    # Create tag category enum
    op.execute("""
        CREATE TYPE tagcategory AS ENUM (
            'industry',
            'location',
            'org_type',
            'funding_purpose',
            'audience',
            'other'
        )
    """)
    
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.Enum('industry', 'location', 'org_type', 'funding_purpose', 'audience', 'other', name='tagcategory'), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('synonyms', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['tags.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    op.create_index(op.f('ix_tags_category'), 'tags', ['category'], unique=False)
    
    # Create grant_tags association table
    op.create_table(
        'grant_tags',
        sa.Column('grant_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['grant_id'], ['grants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('grant_id', 'tag_id')
    )
    
    # Remove old tags column from grants table
    op.drop_column('grants', 'tags')

def downgrade():
    # Add back tags column to grants table
    op.add_column('grants',
        sa.Column('tags', sa.String(length=500), nullable=True)
    )
    
    # Drop tables and enum
    op.drop_table('grant_tags')
    op.drop_table('tags')
    op.execute('DROP TYPE tagcategory') 