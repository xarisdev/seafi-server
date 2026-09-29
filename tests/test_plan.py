import pytest
from src.core.config import settings

@pytest.mark.asyncio
async def test_create_plan(client):
    response = await client.post(
        "/api/v1/plans",
        json={
            "offer_id": "offer-id-123",
            "title": "test-title",
            "description": "test-d",
            "amount_usd": 10.0,
            "duration_hours": 24
        }
    )
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_empty_plans(client):
    response = await client.get("api/v1/plans")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_plans(client):
    response = await client.post(
        "/api/v1/plans",
        json={
            "offer_id": "offer-id-123",
            "title": "test-title",
            "description": "test-d",
            "amount_usd": 10.0,
            "duration_hours": 24
        }
    )
    assert response.status_code == 201

    plan = response.json()
    assert plan["id"] == 1

    response = await client.get(f"api/v1/plans/{plan['id']}")
    assert response.status_code == 200

    _plan = response.json()
    assert _plan["id"] == plan["id"]