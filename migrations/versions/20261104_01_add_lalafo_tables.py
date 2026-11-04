"""Add Lalafo advertisements and durable delivery tables.

Revision ID: 20261104_01
Revises:
Create Date: 2026-11-04
"""

from alembic import op
import sqlalchemy as sa

from src.db.model import Base
from src.models.advertisement import Advertisement
from src.models.advertisement_delivery import AdvertisementDelivery
from src.models.filter import Filter
from src.models.scraper_state import ScraperState


revision = "20261104_01"
down_revision = None
branch_labels = None
depends_on = None


def _column_names(bind: sa.engine.Connection, table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(bind).get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)
    inspector = sa.inspect(bind)

    if inspector.has_table("filters"):
        filter_columns = _column_names(bind, "filters")
        for old_name, new_name in (
            ("deal_type", "ads_type"),
            ("owner_type", "ads_owner"),
            ("price_min", "min_price"),
            ("price_max", "max_price"),
        ):
            if old_name in filter_columns and new_name not in filter_columns:
                op.alter_column("filters", old_name, new_column_name=new_name)
                filter_columns.remove(old_name)
                filter_columns.add(new_name)

        if "property_type" in filter_columns:
            op.alter_column("filters", "property_type", nullable=True)

        if "city" in filter_columns:
            op.execute("UPDATE filters SET city = 'bishkek' WHERE city IS NULL")
            op.alter_column("filters", "city", nullable=False)

    if not inspector.has_table("advertisements"):
        op.create_table(
            "advertisements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ads_id", sa.String(), nullable=False),
            sa.Column("ads_source", sa.Integer(), nullable=False),
            sa.Column("url", sa.String(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("price", sa.Integer(), nullable=True),
            sa.Column("city", sa.String(), nullable=False),
            sa.Column("type", sa.String(), nullable=False),
            sa.Column("owner", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("ads_id", "ads_source", name="uq_id_source"),
        )
    elif "published_at" not in _column_names(bind, "advertisements"):
        op.add_column(
            "advertisements",
            sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not inspector.has_table("advertisement_deliveries"):
        op.create_table(
            "advertisement_deliveries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ads_id", sa.Integer(), sa.ForeignKey("advertisements.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("status", sa.String(), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("ads_id", "user_id", name="uq_ad_delivery_ad_user"),
        )
    else:
        delivery_columns = _column_names(bind, "advertisement_deliveries")
        if "last_attempt_at" not in delivery_columns:
            op.add_column(
                "advertisement_deliveries",
                sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
            )

    if not inspector.has_table("scraper_states"):
        op.create_table(
            "scraper_states",
            sa.Column("key", sa.String(), primary_key=True),
            sa.Column("notifications_enabled_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("scraper_states"):
        op.drop_table("scraper_states")
    if inspector.has_table("advertisement_deliveries"):
        op.drop_table("advertisement_deliveries")
    if inspector.has_table("advertisements"):
        columns = _column_names(bind, "advertisements")
        if "published_at" in columns:
            op.drop_column("advertisements", "published_at")