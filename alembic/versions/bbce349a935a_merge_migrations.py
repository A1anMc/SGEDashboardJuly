"""merge_migrations

Revision ID: bbce349a935a
Revises: dff4b2da4299
Create Date: 2025-07-08 16:10:12.729421

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = 'bbce349a935a'
down_revision: Union[str, None] = 'dff4b2da4299'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
