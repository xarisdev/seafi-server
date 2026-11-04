import logging

from datetime import datetime, timedelta, UTC

from fastapi import HTTPException
from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums.ads_delivery import EnumAdsDeliveryStatus
from ..models.advertisement import Advertisement, AdvertisementRead
from ..models.advertisement_delivery import AdvertisementDelivery
from ..models.subscription import Subscription
from ..models.user import User
from ..models.websocket import AdvertisementDeliveryAck, AdvertisementDeliveryMessage

logger = logging.getLogger("services.advertisement_delivery")

MAX_DELIVERY_ATTEMPTS = 5
DELIVERY_ACK_TIMEOUT = timedelta(minutes=3)
DELIVERY_BATCH_SIZE = 50


async def recover_expired_deliveries(db: AsyncSession) -> None:
    cutoff = datetime.now(UTC) - DELIVERY_ACK_TIMEOUT
    stale = (
        AdvertisementDelivery.status == EnumAdsDeliveryStatus.SENDING,
        AdvertisementDelivery.last_attempt_at < cutoff,
    )
    await db.execute(
        update(AdvertisementDelivery)
        .where(*stale, AdvertisementDelivery.attempts >= MAX_DELIVERY_ATTEMPTS)
        .values(status=EnumAdsDeliveryStatus.FAILED)
    )
    await db.execute(
        update(AdvertisementDelivery)
        .where(*stale, AdvertisementDelivery.attempts < MAX_DELIVERY_ATTEMPTS)
        .values(status=EnumAdsDeliveryStatus.PENDING)
    )


async def expire_ineligible_deliveries(db: AsyncSession) -> None:
    now = datetime.now(UTC)
    published_at = (
        select(Advertisement.published_at)
        .where(Advertisement.id == AdvertisementDelivery.ads_id)
        .scalar_subquery()
    )
    has_eligible_subscription = exists(
        select(Subscription.id).where(
            Subscription.user_id == AdvertisementDelivery.user_id,
            Subscription.started_at.is_not(None),
            Subscription.started_at <= published_at,
            Subscription.expires_at > now,
        )
    )
    await db.execute(
        update(AdvertisementDelivery)
        .where(
            AdvertisementDelivery.status == EnumAdsDeliveryStatus.PENDING,
            ~has_eligible_subscription,
        )
        .values(status=EnumAdsDeliveryStatus.FAILED)
    )


async def claim_pending_deliveries(db: AsyncSession) -> list[int]:
    now = datetime.now(UTC)
    published_at = (
        select(Advertisement.published_at)
        .where(Advertisement.id == AdvertisementDelivery.ads_id)
        .scalar_subquery()
    )
    has_eligible_subscription = exists(
        select(Subscription.id).where(
            Subscription.user_id == AdvertisementDelivery.user_id,
            Subscription.started_at.is_not(None),
            Subscription.started_at <= published_at,
            Subscription.expires_at > now,
        )
    )
    pending_ids = (
        select(AdvertisementDelivery.id)
        .where(
            AdvertisementDelivery.status == EnumAdsDeliveryStatus.PENDING,
            has_eligible_subscription,
        )
        .order_by(AdvertisementDelivery.created_at, AdvertisementDelivery.id)
        .limit(DELIVERY_BATCH_SIZE)
        .with_for_update(skip_locked=True)
        .cte("pending_delivery_ids")
    )
    result = await db.scalars(
        update(AdvertisementDelivery)
        .where(AdvertisementDelivery.id.in_(select(pending_ids.c.id)))
        .values(
            status=EnumAdsDeliveryStatus.SENDING,
            attempts=AdvertisementDelivery.attempts + 1,
            last_attempt_at=now,
        )
        .returning(AdvertisementDelivery.id)
    )
    return list(result.all())


async def load_delivery_messages(
    db: AsyncSession,
    delivery_ids: list[int],
) -> list[AdvertisementDeliveryMessage]:
    if not delivery_ids:
        return []

    result = await db.execute(
        select(AdvertisementDelivery.id, User.telegram_id, Advertisement)
        .join(User, User.id == AdvertisementDelivery.user_id)
        .join(Advertisement, Advertisement.id == AdvertisementDelivery.ads_id)
        .where(AdvertisementDelivery.id.in_(delivery_ids))
    )
    return [
        AdvertisementDeliveryMessage(
            delivery_id=delivery_id,
            telegram_id=telegram_id,
            advertisement=AdvertisementRead.model_validate(advertisement),
        )
        for delivery_id, telegram_id, advertisement in result.all()
    ]


async def acknowledge_delivery(
    db: AsyncSession,
    delivery_id: int,
    payload: AdvertisementDeliveryAck,
) -> None:
    row = (
        await db.execute(
            select(AdvertisementDelivery, User.telegram_id)
            .join(User, User.id == AdvertisementDelivery.user_id)
            .where(AdvertisementDelivery.id == delivery_id)
            .with_for_update()
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Delivery not found")

    delivery, telegram_id = row
    if telegram_id != payload.telegram_id:
        raise HTTPException(status_code=403, detail="Delivery recipient mismatch")

    if delivery.status == EnumAdsDeliveryStatus.SENT:
        return

    if payload.success:
        await db.execute(
            update(AdvertisementDelivery)
            .where(AdvertisementDelivery.id == delivery_id)
            .values(
                status=EnumAdsDeliveryStatus.SENT,
                sent_at=datetime.now(UTC),
            )
        )
        return

    if delivery.status != EnumAdsDeliveryStatus.SENDING:
        return

    next_status = (
        EnumAdsDeliveryStatus.FAILED
        if delivery.attempts >= MAX_DELIVERY_ATTEMPTS
        else EnumAdsDeliveryStatus.PENDING
    )
    await db.execute(
        update(AdvertisementDelivery)
        .where(AdvertisementDelivery.id == delivery_id)
        .values(status=next_status)
    )
    logger.warning(
        "Delivery %s failed on attempt %s: %s",
        delivery_id,
        delivery.attempts,
        payload.error or "unspecified bot delivery error",
    )