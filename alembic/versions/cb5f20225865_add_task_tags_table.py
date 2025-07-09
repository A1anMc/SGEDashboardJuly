"""add_task_tags_table

Revision ID: cb5f20225865
Revises: dff4b2da4299
Create Date: 2024-03-19 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision = 'cb5f20225865'
down_revision = 'dff4b2da4299'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create task_tags table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

    # Create a temporary connection
    connection = op.get_bind()

    # Get all tasks with JSON tags
    tasks = connection.execute(
        sa.text("SELECT id, tags FROM task WHERE tags IS NOT NULL")
    ).fetchall()
    
    for task_id, tags in tasks:
        if isinstance(tags, str):
            try:
                tag_list = json.loads(tags)
            except json.JSONDecodeError:
                tag_list = tags.split(',') if tags else []
        elif isinstance(tags, list):
            tag_list = tags
        else:
            continue
            
        for tag_name in tag_list:
            # Get or create tag
            tag = connection.execute(
                sa.text("SELECT id FROM tags WHERE name = :name"),
                {"name": tag_name}
            ).fetchone()
            
            if not tag:
                result = connection.execute(
                    sa.text("INSERT INTO tags (name) VALUES (:name) RETURNING id"),
                    {"name": tag_name}
                )
                tag_id = result.fetchone()[0]
            else:
                tag_id = tag[0]
            
            # Add task-tag relationship
            connection.execute(
                sa.text(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (:task_id, :tag_id) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"task_id": task_id, "tag_id": tag_id}
            )

    # Drop the old JSON tags column
    with op.batch_alter_table('task') as batch_op:
        batch_op.drop_column('tags')


def downgrade() -> None:
    # Add back the JSON tags column
    with op.batch_alter_table('task') as batch_op:
        batch_op.add_column(sa.Column('tags', sa.JSON(), nullable=True))

    # Create a temporary connection
    connection = op.get_bind()

    # Get all task-tag relationships
    task_tags = connection.execute(
        sa.text("""
            SELECT t.id as task_id, array_agg(tg.name) as tag_names
            FROM task t
            JOIN task_tags tt ON t.id = tt.task_id
            JOIN tags tg ON tt.tag_id = tg.id
            GROUP BY t.id
        """)
    ).fetchall()
    
    # Update tasks with JSON tags
    for task_id, tag_names in task_tags:
        connection.execute(
            sa.text("UPDATE task SET tags = :tags WHERE id = :task_id"),
            {"task_id": task_id, "tags": json.dumps(tag_names)}
        )

    # Drop the task_tags table
    op.drop_table('task_tags')
