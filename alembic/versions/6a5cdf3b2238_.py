"""empty message

Revision ID: 6a5cdf3b2238
Revises: e76f12be9e2f
Create Date: 2025-07-09 21:56:20.692234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a5cdf3b2238'
down_revision: Union[str, None] = 'e76f12be9e2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
