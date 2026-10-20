"""user locale

Revision ID: d5e0f2a3b4c6
Revises: c4d9e1f2a3b5
Create Date: 2026-10-20 16:20:41.552013
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = 'd5e0f2a3b4c6'
down_revision: str | None = 'c4d9e1f2a3b5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('locale', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('locale')
