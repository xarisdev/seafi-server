"""Normalize the legacy maximum-price column name.

Revision ID: 20261104_02
Revises: 20261104_01
Create Date: 2026-11-04
"""

from alembic import op
import sqlalchemy as sa


revision = "20261104_02"
down_revision = "20261104_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("filters")}
    if "price_max" in columns and "max_price" not in columns:
        op.alter_column("filters", "price_max", new_column_name="max_price")


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("filters")}
    if "max_price" in columns and "price_max" not in columns:
        op.alter_column("filters", "max_price", new_column_name="price_max")