from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, update, insert, literal, and_, func

from ..models.plan import Plan
from ..models.invoice import Invoice, EnumInvoiceStatus
from ..models.subscription import Subscription

# ------------ API routes helpers ------------

async def check_active_subscription(
    db: AsyncSession,
    user_id: int
) -> bool:
    return await db.scalar(
        select(exists().where(
            and_(
                Subscription.user_id == user_id,
                Subscription.expires_at.is_not(None),
                Subscription.expires_at > datetime.now(UTC)
            )
        )
    ))

async def get_user_subscriptions(
    db: AsyncSession,
    user_id: int
) -> list[Subscription]:
    result = await db.scalars(
        select(Subscription).where(
            Subscription.user_id == user_id
        )
    )
    return result.all()

async def get_active_user_subscription(
    db: AsyncSession,
    user_id: int
) -> Subscription | None:
    return await db.scalar(
        select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.expires_at.is_not(None),
                Subscription.expires_at > datetime.now(UTC)
            )
        )
    )

async def get_subscription_by_id(
    db: AsyncSession,
    subscription_id: int
) -> Subscription | None:
    return await db.scalar(
        select(Subscription).where(
            Subscription.id == subscription_id
        )
    )

# ------------ Event subscription control ------------

async def activate_user_subscription(
    db: AsyncSession,
    contract_id: str,
    invoice_status: str,
    source: str
):
    timestamp = datetime.now(UTC)

    subquery = (
        update(Invoice)
        .where(Invoice.contract_id == contract_id)
        .values(status=invoice_status)
        .returning(Invoice.id, Invoice.user_id, Invoice.plan_id)
        .cte("invoice")
    )
    query = (
        insert(Subscription)
        .from_select(
            [
                "user_id",
                "plan_id",
                "invoice_id",
                "created_at",
                "started_at",
                "expires_at",
                "source"
            ],
            select(
                subquery.c.user_id,
                subquery.c.plan_id,
                subquery.c.id,
                literal(timestamp),
                literal(timestamp),
                literal(timestamp) + func.make_interval(0, 0, 0, 0, Plan.duration),
                literal(source)
            )
            .join(Plan, Plan.id == subquery.c.plan_id)
        )
    )
    await db.execute(query)