"""Make timestamp tz-aware

Revision ID: 3ef2cf72ca47
Revises: 2aebad861de0
Create Date: 2025-07-01 14:40:09.356732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ef2cf72ca47'
down_revision: Union[str, Sequence[str], None] = '2aebad861de0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('events', 'timestamp',
        type_=sa.TIMESTAMP(timezone=True),
        existing_type=sa.TIMESTAMP(timezone=False)
    )


def downgrade() -> None:
    pass
