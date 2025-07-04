"""add user_id to events

Revision ID: c9fd7c7de7c0
Revises: 5a375ed04159
Create Date: 2025-07-04 08:15:28.410996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, select, column
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = 'c9fd7c7de7c0'
down_revision: Union[str, Sequence[str], None] = '5a375ed04159'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Add the column as nullable for now
    op.add_column('events', sa.Column('user_id', sa.Integer(), nullable=True))

    # 2️⃣ Get the admin user's id (create one if needed)
    bind = op.get_bind()
    session = Session(bind=bind)

    User = table(
        'users',
        sa.Column('id', sa.Integer),
        sa.Column('username', sa.String),
        sa.Column('password_hash', sa.String),
        sa.Column('api_key', sa.String),
        sa.Column('is_admin', sa.Boolean)
    )

    admin_user = session.execute(
        select(User).where(User.c.username == 'lars')
    ).fetchone()

    admin_id = admin_user.id

    # 3️⃣ Update all existing events to point to the admin
    events_table = table('events',
                         column('id', sa.Integer),
                         column('user_id', sa.Integer))
    session.execute(
        events_table.update().values(user_id=admin_id)
    )
    session.commit()

    # 4️⃣ Make the column non-nullable
    op.alter_column('events', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)

    # 5️⃣ Add the foreign key constraint
    op.create_foreign_key('fk_events_user', 'events', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_events_user', 'events', type_='foreignkey')
    op.drop_column('events', 'user_id')
