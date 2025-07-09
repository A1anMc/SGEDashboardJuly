"""merge_heads

Revision ID: 6f1cf19dfd90
Revises: 6a5cdf3b2238, cb5f20225865
Create Date: 2025-07-09 22:09:17.588419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f1cf19dfd90'
down_revision: Union[str, None] = ('6a5cdf3b2238', 'cb5f20225865')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
