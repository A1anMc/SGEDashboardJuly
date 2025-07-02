"""add tag system

Revision ID: 003_add_tag_system
Revises: 002_add_tasks
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_tag_system'
down_revision = '002_add_tasks'
branch_labels = None
depends_on = None

def upgrade():
    # Create tag category enum
    tag_category = postgresql.ENUM('industry', 'location', 'org_type', 'funding_purpose', 'audience',
                                 name='tagcategory')
    tag_category.create(op.get_bind())

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('industry', 'location', 'org_type', 'funding_purpose', 'audience',
                                    name='tagcategory'), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)

    # Create tag_hierarchy table for parent-child relationships
    op.create_table(
        'tag_hierarchy',
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('child_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['child_id'], ['tags.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('parent_id', 'child_id')
    )

    # Create tag_synonyms table
    op.create_table(
        'tag_synonyms',
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('synonym_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['synonym_id'], ['tags.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('tag_id', 'synonym_id')
    )

    # Create grant_tags table
    op.create_table(
        'grant_tags',
        sa.Column('grant_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['grant_id'], ['grants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('grant_id', 'tag_id')
    )

    # Create project_tags table
    op.create_table(
        'project_tags',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'tag_id')
    )

    # Create task_tags table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

def downgrade():
    # Drop all tables in reverse order
    op.drop_table('task_tags')
    op.drop_table('project_tags')
    op.drop_table('grant_tags')
    op.drop_table('tag_synonyms')
    op.drop_table('tag_hierarchy')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
    
    # Drop the enum type
    tag_category = postgresql.ENUM('industry', 'location', 'org_type', 'funding_purpose', 'audience',
                                 name='tagcategory')
    tag_category.drop(op.get_bind()) 