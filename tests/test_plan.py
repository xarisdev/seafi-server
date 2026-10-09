import pytest

from src.core.config import settings

@pytest.mark.asyncio
async def test_create_plan(client):
    response = await client.post(
        "/api/v1/plans",
        json={
            "offer_id": "TEST-OFFER-ID",
            "title": "TEST-TITLE",
            "description": "TEST-DESCRIPTION",
            "amount_usd": 10.0,
            "duration_hours": 24
        }
    )
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_empty_plans(client):
    response = await client.get("api/v1/plans")
    assert response.status_code == 200

    plans = response.json()
    assert len(plans) == 0

@pytest.mark.asyncio
async def test_get_plans(client, subscription_plan):
    response = await client.get("api/v1/plans")
    assert response.status_code == 200

    plans = response.json()
    assert len(plans) == 1

    assert plans[0]["id"] == subscription_plan.id

@pytest.mark.asyncio
async def test_get_plan(client, subscription_plan):
    response = await client.get(f"api/v1/plans/{subscription_plan.id}")
    assert response.status_code == 200

    plan = response.json()
    assert plan["id"] == subscription_plan.id

@pytest.mark.asyncio
async def test_plan_not_found(client):
    response = await client.get("api/v1/plans/123")
    assert response.status_code == 404