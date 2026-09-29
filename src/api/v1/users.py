from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, HTTPException, status, Depends

from ..dependencies import get_user_by_path

from ...db.database import get_db
from ...crud.crud_users import crud_users
from ...models.user import User, UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserRead, status_code=201)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    telegram_id_row = await crud_users.exists(db=db, telegram_id=user.telegram_id)
    if telegram_id_row:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exists")

    created_user = await crud_users.create(db=db, object=user, return_as_model=True, schema_to_select=UserRead)
    return created_user

@router.get("/{telegram_id}", response_model=UserRead)
async def get_user(user: Annotated[User, Depends(get_user_by_path)]):
    return user