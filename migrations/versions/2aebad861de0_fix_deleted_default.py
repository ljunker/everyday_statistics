"""Fix deleted default

Revision ID: 2aebad861de0
Revises: 77c95afd045e
Create Date: 2025-07-01 13:49:36.441458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2aebad861de0'
down_revision: Union[str, Sequence[str], None] = '77c95afd045e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Update existing rows with NULL to FALSE
    op.execute("UPDATE events SET deleted = FALSE WHERE deleted IS NULL;")

    # 2️⃣ Alter the column to NOT NULL with server default
    op.alter_column('events', 'deleted',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.false()
    )


def downgrade() -> None:
    # Downgrade: remove the default and make nullable again
    op.alter_column('events', 'deleted',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None
    )
