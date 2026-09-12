from typing import Annotated, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    HTTPException, status,
    Depends, Header, Body
)

from ...db.models import User
from ...db.database import get_db
from ...models.users import UserRegistrationRequest

from ...app.config import settings

async def verify_secret_key(secret_key: Annotated[str, Header(alias="authorization")]):
    if secret_key != settings.API_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="wk")

router = APIRouter(tags=["users"], dependencies=[Depends(verify_secret_key)])

@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserRegistrationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(User).where(User.telegram_id == request.telegram_id))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exists")

    new_user = User(telegram_id=request.telegram_id, username=request.username)
    db.add(new_user)
    await db.flush()

    return {"status": "success"}

@router.get("/user/{telegram_id}")
async def get_user(
    telegram_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "created_at": user.created_at.isoformat(),
        "subscription_id": user.subscription_id
    }