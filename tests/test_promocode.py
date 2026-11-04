import pytest

from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio
async def test_create_promocode(client, user, subscription_plan):
    response = await client.post(
        "/api/v1/promocodes",
        json={
            "code": "WELCOME10",
            "plan_id": subscription_plan.id,
            "duration_hours": 48,
            "usage_limit": 10,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        }
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == "WELCOME10"
    assert payload["usage_limit"] == 10


@pytest.mark.asyncio
async def test_activate_promocode_creates_subscription(client, user, subscription_plan):
    response = await client.post(
        "/api/v1/promocodes",
        json={
            "code": "WELCOME10",
            "plan_id": subscription_plan.id,
            "duration_hours": 48,
            "usage_limit": 10,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        }
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/promocodes/WELCOME10/activate",
        params={"telegram_id": user.telegram_id}
    )
    assert response.status_code == 200
    subscription = response.json()
    assert subscription["user_id"] == user.id
    assert subscription["plan_id"] == subscription_plan.id
    assert subscription["invoice_id"] is None
    assert subscription["source"] == "promo:WELCOME10"
    started_at = datetime.fromisoformat(subscription["started_at"])
    expires_at = datetime.fromisoformat(subscription["expires_at"])
    assert expires_at - started_at == timedelta(hours=48)


@pytest.mark.asyncio
async def test_promocode_can_be_used_only_once_per_user(client, user, subscription_plan):
    response = await client.post(
        "/api/v1/promocodes",
        json={
            "code": "ONCEONLY",
            "plan_id": subscription_plan.id,
            "duration_hours": 48,
            "usage_limit": 10,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        }
    )
    assert response.status_code == 201

    first = await client.post(
        "/api/v1/promocodes/ONCEONLY/activate",
        params={"telegram_id": user.telegram_id}
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/v1/promocodes/ONCEONLY/activate",
        params={"telegram_id": user.telegram_id}
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_promocode_activation_is_blocked_by_pending_payment(client, user, subscription_plan):
    invoice = await client.post(
        f"/api/v1/payments/invoices?plan_id={subscription_plan.id}&telegram_id={user.telegram_id}"
    )
    assert invoice.status_code == 201

    promocode = await client.post(
        "/api/v1/promocodes",
        json={"code": "PENDINGPAYMENT", "plan_id": subscription_plan.id, "duration_hours": 48}
    )
    assert promocode.status_code == 201

    activation = await client.post(
        "/api/v1/promocodes/PENDINGPAYMENT/activate",
        params={"telegram_id": user.telegram_id}
    )
    assert activation.status_code == 400

    active_subscription = await client.get(
        f"/api/v1/subscriptions/active?telegram_id={user.telegram_id}"
    )
    assert active_subscription.status_code == 200
    assert active_subscription.json() is None


@pytest.mark.asyncio
async def test_active_promocode_subscription_blocks_payment_invoice(client, user, subscription_plan):
    promocode = await client.post(
        "/api/v1/promocodes",
        json={"code": "PROMOFIRST", "plan_id": subscription_plan.id, "duration_hours": 48}
    )
    assert promocode.status_code == 201

    activation = await client.post(
        "/api/v1/promocodes/PROMOFIRST/activate",
        params={"telegram_id": user.telegram_id}
    )
    assert activation.status_code == 200

    invoice = await client.post(
        f"/api/v1/payments/invoices?plan_id={subscription_plan.id}&telegram_id={user.telegram_id}"
    )
    assert invoice.status_code == 400
