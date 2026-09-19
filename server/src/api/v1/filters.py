from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, HTTPException, status, Depends
from ..dependencies import verify_secret_key

from ...db.database import get_db
from ...crud.crud_users import crud_users
from ...crud.crud_filters import crud_filters
from ...models.user import UserRead
from ...models.filter import FilterCreate, FilterRead, FilterUpdate

from ...services.filters_queue import filters_queue

router = APIRouter(prefix="/filters", tags=["Filters"], dependencies=[Depends(verify_secret_key)])

@router.post("/create", response_model=FilterRead, status_code=201)
async def new_filter(
    filter_create: FilterCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    telegram_id_row = await crud_filters.exists(db=db, telegram_id=filter_create.telegram_id)
    if telegram_id_row:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Filter already exists"
        )

    created_filter = await crud_filters.create(db=db, object=filter_create, return_as_model=FilterRead)
    return created_filter

@router.patch("/patch", response_model=FilterRead, status_code=202)
async def patch_filter(
    filter_update: FilterUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    db_filter = await crud_filters.exists(db=db, telegram_id=filter_update.telegram_id)
    if not db_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filter not found"
        )

    user: UserRead = await crud_users.get(
        db=db,
        schema_to_select=UserRead,
        one_or_none=True,
        telegram_id=filter_update.telegram_id
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_premium: # TODO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied"
        )

    updated_filter: FilterRead = await crud_filters.update(
        db=db,
        object=filter_update,
        telegram_id=filter_update.telegram_id
    )
    if updated_filter.price_min != -1:
        await filters_queue.add_filter(updated_filter.id)
    else:
        await filters_queue.remove_filter(updated_filter.id)

    return updated_filter