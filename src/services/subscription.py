import logging

from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_subscriptions import UserSubscriptionRead, UserSubscriptionUpdate
from ..models.subscription_plans import SubscriptionPlanRead
from ..crud.crud_subscriptions import crud_subscriptions
from ..crud.crud_plans import crud_plans

logger = logging.getLogger("services.subscription")

async def _get_subscription_exists(
    db: AsyncSession,
    invoice_id: str
) -> UserSubscriptionRead:
    subscription = await crud_subscriptions.get(
        db=db,
        schema_to_select=UserSubscriptionRead,
        return_as_model=True,
        one_or_none=True,
        invoice_id=invoice_id
    )
    if subscription is None:
        raise ValueError(f"UserSubscription with invoice_id: {invoice_id} not found")

    return subscription

async def activate_user_subscription(
    db: AsyncSession,
    invoice_id: str,
    status: str
) -> UserSubscriptionRead:
    subscription = await _get_subscription_exists(db=db, invoice_id=invoice_id)
    
    if subscription.status != "new":
        raise ValueError("Subscription already processed")

    plan = await crud_plans.get(
        db=db,
        schema_to_select=SubscriptionPlanRead,
        return_as_model=True,
        one_or_none=True,
        id=subscription.plan_id
    )
    if plan is None:
        raise ValueError("Subscription plan not found")

    timestamp = datetime.now(timezone.utc)
    model = UserSubscriptionUpdate(
        started_at=timestamp,
        expires_at=timestamp + timedelta(hours=plan.duration_hours),
        status=status
    )

    return await crud_subscriptions.update(
        db=db,
        object=model,
        invoice_id=invoice_id,
        schema_to_select=UserSubscriptionRead,
        return_as_model=True
    )

async def failed_user_subscription(
    db: AsyncSession,
    invoice_id: str,
    status: str
) -> UserSubscriptionRead:
    _ = await _get_subscription_exists(db=db, invoice_id=invoice_id)

    subscription_update = UserSubscriptionUpdate(
        started_at=None,
        expires_at=None,
        status=status
    )

    return await crud_subscriptions.update(
        db=db,
        object=subscription_update,
        invoice_id=invoice_id,
        schema_to_select=UserSubscriptionRead,
        return_as_model=True
    )