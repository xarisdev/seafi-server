import pytest

from src.core.config import settings

@pytest.mark.asyncio
async def test_user_not_found(client):
    response = await client.get(
        f"/api/v1/users/{settings.TEST_TELEGRAM_ID}"
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_user_without_fields(client):
    response = await client.post(
        "/api/v1/users",
        json={}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user_with_wrong_field(client):
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": f"wrong{settings.TEST_TELEGRAM_ID}field"
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": settings.TEST_TELEGRAM_ID
        }
    )
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_existing_user(client, user):
    response = await client.post(
        "/api/v1/users",
        json={
            "telegram_id": user.telegram_id
        }
    )
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_user_exists(client, user):
    response = await client.get(
        f"/api/v1/users/{user.telegram_id}"
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_user_by_id(client, user):
    response = await client.get(
        f"/api/v1/users?id={user.id}"
    )
    assert response.status_code == 200
    assert response.json()["telegram_id"] == user.telegram_id