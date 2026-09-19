from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, HTTPException, status, Depends
from ..dependencies import verify_secret_key

from ...db.database import get_db
from ...crud.crud_users import crud_users
from ...models.user import UserCreate, UserRead

router = APIRouter(tags=["users"], dependencies=[Depends(verify_secret_key)])

@router.post("/users", response_model=UserRead, status_code=201)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    telegram_id_row = await crud_users.exists(db=db, telegram_id=user.telegram_id)
    if telegram_id_row:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exists")

    _created_user = await crud_users.create(db=db, object=user, return_as_model=UserRead)
    return _created_user

@router.get("/users/{telegram_id}", response_model=UserRead)
async def get_user(
    telegram_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await crud_users.get(
        db=db,
        schema_to_select=UserRead,
        one_or_none=True,
        telegram_id=telegram_id
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user