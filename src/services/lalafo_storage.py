from datetime import datetime, UTC

from sqlalchemy import DateTime, case, func, literal, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums.ads_delivery import EnumAdsDeliveryStatus
from ..enums.advertisement import EnumAdsOwner, EnumAdsSourceId, EnumAdsType
from ..models.advertisement import Advertisement
from ..models.advertisement_delivery import AdvertisementDelivery
from ..models.filter import Filter
from ..models.scraper_state import ScraperState
from ..models.subscription import Subscription
from ..models.user import User
from ..integrations.lalafo.parser import LalafoListing


NOTIFICATION_STATE_KEY = "lalafo-notifications"


async def ensure_notification_baseline(db: AsyncSession) -> datetime:
    state = await db.get(ScraperState, NOTIFICATION_STATE_KEY)
    if state is None:
        state = ScraperState(
            key=NOTIFICATION_STATE_KEY,
            notifications_enabled_at=datetime.now(UTC),
        )
        db.add(state)
        await db.flush()
    return state.notifications_enabled_at


async def upsert_lalafo_listings(
    db: AsyncSession,
    listings: list[LalafoListing],
) -> int:
    if not listings:
        return 0

    listing_ids = {listing.ads_id for listing in listings}
    existing_ids = set(
        (
            await db.scalars(
                select(Advertisement.ads_id).where(
                    Advertisement.ads_source == EnumAdsSourceId.LALAFO,
                    Advertisement.ads_id.in_(listing_ids),
                )
            )
        ).all()
    )

    now = datetime.now(UTC)
    rows = [
        {
            "ads_id": listing.ads_id,
            "ads_source": EnumAdsSourceId.LALAFO,
            "url": listing.url,
            "title": listing.title,
            "price": listing.price,
            "city": listing.city,
            "type": EnumAdsType.RENT,
            "owner": listing.owner,
            "created_at": now,
            "last_seen_at": now,
            "published_at": listing.published_at,
        }
        for listing in listings
    ]
    statement = insert(Advertisement).values(rows)
    excluded = statement.excluded
    statement = statement.on_conflict_do_update(
        index_elements=[Advertisement.ads_id, Advertisement.ads_source],
        set_={
            "url": excluded.url,
            "title": excluded.title,
            "price": excluded.price,
            "city": excluded.city,
            "type": excluded.type,
            "owner": case(
                (excluded.owner == EnumAdsOwner.ANY.value, Advertisement.owner),
                else_=excluded.owner,
            ),
            "last_seen_at": now,
            "published_at": func.coalesce(excluded.published_at, Advertisement.published_at),
        },
    )
    await db.execute(statement)
    return len(listing_ids - existing_ids)


async def create_matching_deliveries(db: AsyncSession) -> int:
    state = await db.get(ScraperState, NOTIFICATION_STATE_KEY)
    if state is None:
        return 0

    now = datetime.now(UTC)
    conditions = [
        Advertisement.ads_source == EnumAdsSourceId.LALAFO,
        Advertisement.type == EnumAdsType.RENT,
        Advertisement.published_at.is_not(None),
        Advertisement.published_at >= state.notifications_enabled_at,
        Advertisement.published_at >= Subscription.started_at,
        Subscription.started_at.is_not(None),
        Subscription.expires_at > now,
        or_(Filter.ads_type.is_(None), Filter.ads_type == Advertisement.type),
        or_(
            Filter.ads_owner.is_(None),
            Filter.ads_owner == EnumAdsOwner.ANY,
            Filter.ads_owner == Advertisement.owner,
        ),
    ]

    conditions.extend(
        [
            Filter.min_price.is_(None) | (Advertisement.price >= Filter.min_price),
            Filter.max_price.is_(None) | (Advertisement.price <= Filter.max_price),
        ]
    )

    candidates = (
        select(
            Advertisement.id,
            Filter.user_id,
            literal(EnumAdsDeliveryStatus.PENDING.value),
            literal(0),
            literal(now),
            literal(None, type_=DateTime(timezone=True)),
            literal(None, type_=DateTime(timezone=True)),
        )
        .select_from(Advertisement)
        .join(Filter, func.lower(Filter.city) == func.lower(Advertisement.city))
        .join(Subscription, Subscription.user_id == Filter.user_id)
        .where(*conditions)
        .distinct()
    )
    statement = (
        insert(AdvertisementDelivery)
        .from_select(
            [
                "ads_id",
                "user_id",
                "status",
                "attempts",
                "created_at",
                "sent_at",
                "last_attempt_at",
            ],
            candidates,
        )
        .on_conflict_do_nothing(constraint="uq_ad_delivery_ad_user")
        .returning(AdvertisementDelivery.id)
    )
    result = await db.scalars(statement)
    return len(result.all())