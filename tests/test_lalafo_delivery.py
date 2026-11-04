from datetime import datetime, timedelta, UTC

import pytest
from sqlalchemy import select

from src.enums.ads_delivery import EnumAdsDeliveryStatus
from src.enums.advertisement import EnumAdsOwner, EnumAdsSourceId, EnumAdsType
from src.models.advertisement import Advertisement
from src.models.advertisement_delivery import AdvertisementDelivery
from src.models.filter import Filter
from src.models.scraper_state import ScraperState
from src.models.subscription import Subscription
from src.models.user import User
from src.integrations.lalafo.parser import LalafoListing
from src.services.advertisement_delivery import (
    claim_pending_deliveries,
    expire_ineligible_deliveries,
)
from src.services.lalafo_storage import (
    NOTIFICATION_STATE_KEY,
    create_matching_deliveries,
    upsert_lalafo_listings,
)


def _advertisement(ads_id: str, published_at: datetime, owner=EnumAdsOwner.AGENT) -> Advertisement:
    return Advertisement(
        ads_id=ads_id,
        ads_source=EnumAdsSourceId.LALAFO,
        url=f"https://lalafo.kg/bishkek/ads/test-id-{ads_id}",
        title="Квартира долгосрочно",
        price=35000,
        city="bishkek",
        type=EnumAdsType.RENT,
        owner=owner,
        published_at=published_at,
    )


@pytest.mark.asyncio
async def test_matching_requires_subscription_filter_and_recent_publication(db_session, user):
    now = datetime.now(UTC)
    paid_user = user
    unpaid_user = User(telegram_id=user.telegram_id + 1)
    sell_filter_user = User(telegram_id=user.telegram_id + 2)
    db_session.add_all([unpaid_user, sell_filter_user])
    await db_session.flush()

    db_session.add_all(
        [
            ScraperState(
                key=NOTIFICATION_STATE_KEY,
                notifications_enabled_at=now - timedelta(hours=1),
            ),
            Subscription(
                user_id=paid_user.id,
                plan_id=None,
                invoice_id=None,
                started_at=now - timedelta(hours=2),
                expires_at=now + timedelta(days=1),
                source="test-payment",
            ),
            Subscription(
                user_id=sell_filter_user.id,
                plan_id=None,
                invoice_id=None,
                started_at=now - timedelta(hours=2),
                expires_at=now + timedelta(days=1),
                source="test-payment",
            ),
            Filter(
                user_id=paid_user.id,
                city="bishkek",
                ads_type=EnumAdsType.RENT,
                ads_owner=EnumAdsOwner.AGENT,
                max_price=50000,
            ),
            Filter(
                user_id=unpaid_user.id,
                city="bishkek",
                ads_type=EnumAdsType.RENT,
                ads_owner=EnumAdsOwner.AGENT,
                max_price=50000,
            ),
            Filter(
                user_id=sell_filter_user.id,
                city="bishkek",
                ads_type=EnumAdsType.SELL,
                ads_owner=EnumAdsOwner.AGENT,
                max_price=50000,
            ),
            _advertisement("new-listing", now - timedelta(minutes=20)),
            _advertisement("old-listing", now - timedelta(days=2)),
            _advertisement("owner-listing", now - timedelta(minutes=20), EnumAdsOwner.OWNER),
        ]
    )
    await db_session.flush()

    created = await create_matching_deliveries(db_session)
    created_again = await create_matching_deliveries(db_session)
    deliveries = (
        await db_session.scalars(select(AdvertisementDelivery))
    ).all()

    assert created == 1
    assert created_again == 0
    assert len(deliveries) == 1
    assert deliveries[0].user_id == paid_user.id
    assert deliveries[0].status == EnumAdsDeliveryStatus.PENDING


@pytest.mark.asyncio
async def test_upsert_deduplicates_and_preserves_known_owner(db_session):
    published_at = datetime.now(UTC) - timedelta(minutes=10)
    agent_listing = LalafoListing(
        ads_id="same-listing",
        url="https://lalafo.kg/bishkek/ads/test-id-same-listing",
        title="Original title",
        price=35000,
        city="bishkek",
        owner=EnumAdsOwner.AGENT,
        published_at=published_at,
    )
    city_listing = LalafoListing(
        ads_id="same-listing",
        url=agent_listing.url,
        title="Updated title",
        price=36000,
        city="bishkek",
        owner=EnumAdsOwner.ANY,
        published_at=published_at,
    )

    assert await upsert_lalafo_listings(db_session, [agent_listing]) == 1
    assert await upsert_lalafo_listings(db_session, [city_listing]) == 0

    stored = await db_session.scalar(
        select(Advertisement).where(Advertisement.ads_id == "same-listing")
    )
    assert stored is not None
    assert stored.title == "Updated title"
    assert stored.price == 36000
    assert stored.owner == EnumAdsOwner.AGENT


@pytest.mark.asyncio
async def test_pending_delivery_is_closed_after_subscription_expires(db_session, user):
    now = datetime.now(UTC)
    advertisement = _advertisement("expired-subscription-listing", now - timedelta(hours=1))
    db_session.add(advertisement)
    await db_session.flush()

    db_session.add_all(
        [
            Subscription(
                user_id=user.id,
                plan_id=None,
                invoice_id=None,
                started_at=now - timedelta(days=1),
                expires_at=now - timedelta(minutes=1),
                source="expired-test-payment",
            ),
            AdvertisementDelivery(
                ads_id=advertisement.id,
                user_id=user.id,
                status=EnumAdsDeliveryStatus.PENDING,
                attempts=0,
            ),
        ]
    )
    await db_session.flush()

    await expire_ineligible_deliveries(db_session)
    pending_ids = await claim_pending_deliveries(db_session)
    delivery = await db_session.scalar(
        select(AdvertisementDelivery).where(AdvertisementDelivery.ads_id == advertisement.id)
    )

    assert pending_ids == []
    assert delivery is not None
    assert delivery.status == EnumAdsDeliveryStatus.FAILED


@pytest.mark.asyncio
async def test_ack_marks_delivery_sent(client, db_session, user):
    now = datetime.now(UTC)
    advertisement = _advertisement("ack-listing", now - timedelta(minutes=10))
    db_session.add(advertisement)
    await db_session.flush()

    delivery = AdvertisementDelivery(
        ads_id=advertisement.id,
        user_id=user.id,
        status=EnumAdsDeliveryStatus.SENDING,
        attempts=1,
        last_attempt_at=now,
    )
    db_session.add(delivery)
    await db_session.flush()

    response = await client.post(
        f"/api/v1/deliveries/{delivery.id}/ack",
        json={"telegram_id": user.telegram_id, "success": True},
    )

    assert response.status_code == 204
    await db_session.refresh(delivery)
    assert delivery.status == EnumAdsDeliveryStatus.SENT
    assert delivery.sent_at is not None


@pytest.mark.asyncio
async def test_ack_rejects_wrong_recipient(client, db_session, user):
    now = datetime.now(UTC)
    advertisement = _advertisement("wrong-recipient-listing", now - timedelta(minutes=10))
    db_session.add(advertisement)
    await db_session.flush()
    delivery = AdvertisementDelivery(
        ads_id=advertisement.id,
        user_id=user.id,
        status=EnumAdsDeliveryStatus.SENDING,
        attempts=1,
        last_attempt_at=now,
    )
    db_session.add(delivery)
    await db_session.flush()

    response = await client.post(
        f"/api/v1/deliveries/{delivery.id}/ack",
        json={"telegram_id": user.telegram_id + 100, "success": True},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_failed_ack_requeues_delivery(client, db_session, user):
    now = datetime.now(UTC)
    advertisement = _advertisement("retry-listing", now - timedelta(minutes=10))
    db_session.add(advertisement)
    await db_session.flush()
    delivery = AdvertisementDelivery(
        ads_id=advertisement.id,
        user_id=user.id,
        status=EnumAdsDeliveryStatus.SENDING,
        attempts=1,
        last_attempt_at=now,
    )
    db_session.add(delivery)
    await db_session.flush()

    response = await client.post(
        f"/api/v1/deliveries/{delivery.id}/ack",
        json={
            "telegram_id": user.telegram_id,
            "success": False,
            "error": "Telegram temporarily unavailable",
        },
    )

    assert response.status_code == 204
    await db_session.refresh(delivery)
    assert delivery.status == EnumAdsDeliveryStatus.PENDING