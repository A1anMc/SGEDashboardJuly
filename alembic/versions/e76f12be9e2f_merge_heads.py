"""merge_heads

Revision ID: e76f12be9e2f
Revises: 954bc2c034cf, bbce349a935a
Create Date: 2025-07-09 15:46:18.343209

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = 'e76f12be9e2f'
down_revision: Union[str, None] = ('954bc2c034cf', 'bbce349a935a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
