import logging

from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions.http_exceptions import BadRequestException, NotFoundException
from ..models.user_subscriptions import UserSubscriptionRead, UserSubscriptionUpdate
from ..models.subscription_plans import SubscriptionPlanRead
from ..models.user import UserRead, UserUpdate
from ..crud.crud_subscriptions import crud_subscriptions
from ..crud.crud_plans import crud_plans
from ..crud.crud_users import crud_users

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

    user = await crud_users.get(
        db=db,
        id=subscription.user_id,
        schema_to_select=UserRead,
        return_as_model=True
    )
    timestamp = datetime.now(timezone.utc)
    expires_at = timestamp + timedelta(hours=plan.duration_hours)

    if user.trial_expires_at is not None:
        if user.trial_expires_at.astimezone(timezone.utc) > timestamp:
            trial = user.trial_expires_at.astimezone(timezone.utc) - timestamp
            expires_at += trial
            
            await crud_users.update(
                db=db,
                object=UserUpdate(trial_expires_at=None),
                id=user.id
            )

    model = UserSubscriptionUpdate(
        started_at=timestamp,
        expires_at=expires_at,
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

async def check_active_subscription(
    db: AsyncSession,
    user_id: int
):
    now = datetime.now(timezone.utc)

    subs = await crud_subscriptions.get_multi(
        db=db,
        user_id=user_id,
        status="success",
        schema_to_select=UserSubscriptionRead,
        return_as_model=True
    )
    for sub in subs.get('data'):
        if sub.expires_at > now:
            raise BadRequestException("User already has an active subscription")
        else:
            sub.status = "expired"
            sub_update = UserSubscriptionUpdate(**sub)
            await crud_subscriptions.update(
                db=db,
                object=sub_update,
                id=sub.id
            )

async def active_subscription(
    db: AsyncSession,
    user_id: int,
) -> UserSubscriptionRead:
    subs = await crud_subscriptions.get_multi(
        db=db,
        user_id=user_id,
        status="success",
        schema_to_select=UserSubscriptionRead,
        return_as_model=True
    )
    now = datetime.now(timezone.utc)

    actual_started_at: datetime = None
    total_duration: timedelta = timedelta()

    last_active_id = None

    for sub in subs.get('data'):
        if sub.expires_at.astimezone(timezone.utc) < now:
            sub.status = "expired"
            
            await crud_subscriptions.update(
                db=db,
                id=sub.id,
                object=UserSubscriptionUpdate(
                    status=sub.status
                )
            )
            
            continue

        if actual_started_at is None:
            actual_started_at = sub.started_at

        if sub.started_at < actual_started_at:
            actual_started_at = sub.started_at

        total_duration += sub.expires_at.astimezone(timezone.utc) - sub.started_at.astimezone(timezone.utc)

        last_active_id = sub.id

        await crud_subscriptions.update(
            db=db,
            id=sub.id,
            object=UserSubscriptionUpdate(
                status="merge"
            )
        )

    if last_active_id is not None:
        subscription = await crud_subscriptions.update(
            db=db,
            id=last_active_id,
            object=UserSubscriptionUpdate(
                started_at=actual_started_at,
                expires_at=actual_started_at + total_duration,
                status="success"
            ),
            schema_to_select=UserSubscriptionRead,
            return_as_model=True,
        )
        return subscription
        
    raise NotFoundException("User has not active subscription")