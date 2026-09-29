import pytest
from src.core.config import settings

@pytest.mark.asyncio
async def test_create_link(client):
    response = await client.post(
        "/api/v1/users",
        json={"telegram_id": settings.TEST_TELEGRAM_ID}
    )
    assert response.status_code == 201
    assert response.json()["telegram_id"] == settings.TEST_TELEGRAM_ID

    response = await client.get(
        "/api/v1/products"
    )
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

    invoice_schema = response.json()
    assert invoice_schema["status"] == "new"