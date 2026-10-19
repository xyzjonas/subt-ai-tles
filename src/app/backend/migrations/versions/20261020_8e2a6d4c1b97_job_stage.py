"""job stage

Revision ID: 8e2a6d4c1b97
Revises: 5b1f3c9a7d42
Create Date: 2026-10-20 10:31:09.204417
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '8e2a6d4c1b97'
down_revision: str | None = '5b1f3c9a7d42'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stage', sa.Enum('recognizing', 'summarizing', 'translating', name='jobstage', native_enum=False, length=16), server_default='recognizing', nullable=False))
        batch_op.add_column(sa.Column('summary_status', sa.String(), nullable=True))
        batch_op.drop_column('step')


def downgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('step', sa.VARCHAR(), nullable=True))
        batch_op.drop_column('summary_status')
        batch_op.drop_column('stage')
