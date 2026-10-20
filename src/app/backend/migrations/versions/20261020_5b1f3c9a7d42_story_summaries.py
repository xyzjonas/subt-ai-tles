"""story summaries

Revision ID: 5b1f3c9a7d42
Revises: ca7e927597f6
Create Date: 2026-10-20 09:12:44.518302
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "5b1f3c9a7d42"
down_revision: str | None = "ca7e927597f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "story_summaries",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("story_summaries")
