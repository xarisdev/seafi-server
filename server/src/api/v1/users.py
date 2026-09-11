from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, HTTPException, Depends, status

from ...db.models import User
from ...db.database import get_db
from ...models.users import UserRegistrationRequest

from ...app.config import settings

router = APIRouter(tags=["users"])

@router.get("/ping")
async def ping(): return {"status": "pong"}

@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserRegistrationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if request.secret_key != settings.API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong key")

    result = await db.execute(select(User).where(User.telegram_id == request.telegram_id))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {"status": "Already exists"}

    new_user = User(telegram_id=request.telegram_id, username=request.username)
    db.add(new_user)
    await db.flush()
    return {"status": "success"}