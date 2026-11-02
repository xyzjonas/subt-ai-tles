"""membership requests and default quota

Revision ID: b2d4f6a8c0e1
Revises: a1c3e5f7b9d2
Create Date: 2026-11-02 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "b2d4f6a8c0e1"
down_revision: str | None = "a1c3e5f7b9d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "membership_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("details", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="membershiprequeststatus", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("membership_requests", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_membership_requests_email"), ["email"], unique=False)
        batch_op.create_index(batch_op.f("ix_membership_requests_status"), ["status"], unique=False)

    with op.batch_alter_table("app_settings", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("default_monthly_quota", sa.Integer(), server_default="1000", nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("app_settings", schema=None) as batch_op:
        batch_op.drop_column("default_monthly_quota")

    with op.batch_alter_table("membership_requests", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_membership_requests_status"))
        batch_op.drop_index(batch_op.f("ix_membership_requests_email"))
    op.drop_table("membership_requests")
