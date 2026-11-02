"""request folders and archiving

Revision ID: a1c3e5f7b9d2
Revises: e6f1a3b4c5d7
Create Date: 2026-11-02 10:21:07.402816
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "a1c3e5f7b9d2"
down_revision: str | None = "e6f1a3b4c5d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "folders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_folders_owner_id"), "folders", ["owner_id"], unique=False)
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("folder_id", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_index(batch_op.f("ix_jobs_folder_id"), ["folder_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_jobs_folder_id_folders",
            "folders",
            ["folder_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.drop_constraint("fk_jobs_folder_id_folders", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_jobs_folder_id"))
        batch_op.drop_column("archived_at")
        batch_op.drop_column("folder_id")
    op.drop_index(op.f("ix_folders_owner_id"), table_name="folders")
    op.drop_table("folders")
