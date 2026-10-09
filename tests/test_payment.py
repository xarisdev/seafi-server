import pytest

from datetime import datetime, timezone

from src.core.config import settings

@pytest.mark.asyncio
async def test_create_link(client, user):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200

    first_product = response.json()[0]
    assert "/ seafi" in first_product["title"]

    response = await client.post(
        "/api/v1/plans",
        json={
            "offer_id": first_product["offer_id"],
            "title": "test-title",
            "description": "test-d",
            "amount_usd": 10.0,
            "duration_hours": 24
        }
    )
    assert response.status_code == 201
    plan = response.json()

    response = await client.post(
        f"/api/v1/payments/create-link/{plan['id']}?telegram_id={settings.TEST_TELEGRAM_ID}"
    )
    assert response.status_code == 201

    invoice_schema = response.json()["invoice"]
    assert invoice_schema["status"] == "new"

@pytest.mark.asyncio
async def test_not_found_subscription(client, user):
    response = await client.get(
        f"/api/v1/subscriptions/active?telegram_id={user.telegram_id}"
    )
    assert response.status_code == 200
    assert response.json() == None

@pytest.mark.asyncio
async def test_get_success_subscription(client, user):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200

    first_product = response.json()[0]
    assert "/ seafi" in first_product["title"]

    response = await client.post(
        "/api/v1/plans",
        json={
            "offer_id": first_product["offer_id"],
            "title": "test-title",
            "description": "test-d",
            "amount_usd": 10.0,
            "duration_hours": 24
        }
    )
    assert response.status_code == 201
    plan = response.json()

    response = await client.post(
        f"/api/v1/payments/create-link/{plan['id']}?telegram_id={settings.TEST_TELEGRAM_ID}"
    )
    assert response.status_code == 201
    invoice_schema = response.json()["invoice"]
    assert invoice_schema["status"] == "new"

    response = await client.post(
        "api/v1/webhook/lava",
        json={
            "eventType": "payment.success",
            "contractId": invoice_schema["id"],
            "buyer": {
                "email": f"user_{settings.TEST_TELEGRAM_ID}@xaris.tech"
            },
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    assert response.status_code == 200

    response = await client.get(
        f"/api/v1/subscriptions/active?telegram_id={settings.TEST_TELEGRAM_ID}"
    )
    assert response.status_code == 200
    
    assert response.json()["status"] == "success"