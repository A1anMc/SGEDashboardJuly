"""merge task_related_tables and update_grants_table

Revision ID: 229176025b48
Revises: 001_7_create_task_related_tables, 004_update_grants_table
Create Date: 2025-07-08 15:40:03.321667

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '229176025b48'
down_revision: Union[str, None] = ('001_7_create_task_related_tables', '004_update_grants_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
