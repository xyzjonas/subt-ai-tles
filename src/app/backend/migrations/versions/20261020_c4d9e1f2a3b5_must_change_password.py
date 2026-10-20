"""must change password

Revision ID: c4d9e1f2a3b5
Revises: 8e2a6d4c1b97
Create Date: 2026-10-20 14:02:11.318204
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = 'c4d9e1f2a3b5'
down_revision: str | None = '8e2a6d4c1b97'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('must_change_password', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('must_change_password')
