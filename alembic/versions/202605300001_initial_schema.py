"""initial schema

Revision ID: 202605300001
Revises:
Create Date: 2026-05-30 23:20:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "202605300001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "portfolios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "name", name="uq_portfolio_owner_name"),
    )
    op.create_index(op.f("ix_portfolios_id"), "portfolios", ["id"], unique=False)

    op.create_table(
        "holdings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("portfolio_id", "symbol", name="uq_holding_portfolio_symbol"),
    )
    op.create_index(op.f("ix_holdings_id"), "holdings", ["id"], unique=False)
    op.create_index(op.f("ix_holdings_portfolio_id"), "holdings", ["portfolio_id"], unique=False)

    op.create_table(
        "target_allocations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("target_percent", sa.Numeric(precision=7, scale=4), nullable=False),
        sa.CheckConstraint("target_percent >= 0 AND target_percent <= 100", name="ck_target_percent"),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("portfolio_id", "symbol", name="uq_target_portfolio_symbol"),
    )
    op.create_index(op.f("ix_target_allocations_id"), "target_allocations", ["id"], unique=False)
    op.create_index(
        op.f("ix_target_allocations_portfolio_id"),
        "target_allocations",
        ["portfolio_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_target_allocations_portfolio_id"), table_name="target_allocations")
    op.drop_index(op.f("ix_target_allocations_id"), table_name="target_allocations")
    op.drop_table("target_allocations")
    op.drop_index(op.f("ix_holdings_portfolio_id"), table_name="holdings")
    op.drop_index(op.f("ix_holdings_id"), table_name="holdings")
    op.drop_table("holdings")
    op.drop_index(op.f("ix_portfolios_id"), table_name="portfolios")
    op.drop_table("portfolios")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
