"""job source language inferred

Revision ID: e6f1a3b4c5d7
Revises: d5e0f2a3b4c6
Create Date: 2026-10-20 17:05:12.318204
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "e6f1a3b4c5d7"
down_revision: str | None = "d5e0f2a3b4c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.alter_column("source_lang", existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE jobs SET source_lang = target_lang WHERE source_lang IS NULL")
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.alter_column("source_lang", existing_type=sa.VARCHAR(), nullable=False)
