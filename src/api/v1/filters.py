from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from ...core.exceptions.http_exceptions import NotFoundException

from ...db.database import get_db
from ...crud.crud_filters import crud_filters
from ...models.filter import FilterRead, FilterUpdate

router = APIRouter(prefix="/filters", tags=["Filters"])

@router.get("/{user_id}", response_model=FilterRead)
async def get_filter(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    db_filter = await crud_filters.get(
        db=db,
        user_id=user_id,
        schema_to_select=FilterRead,
        return_as_model=True,
        one_or_none=True
    )
    if db_filter is None:
        raise NotFoundException("Filter not found")

    return db_filter

@router.patch("/{user_id}", response_model=FilterRead)
async def patch_filter(
    user_id: int,
    filter_update: FilterUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    db_filter = await crud_filters.get(
        db=db,
        user_id=user_id,
        schema_to_select=FilterRead,
        return_as_model=True,
        one_or_none=True
    )
    if db_filter is None:
        raise NotFoundException("Filter not found")
    
    patched_filter = await crud_filters.update(
        db=db,
        object=filter_update,
        id=db_filter.id,
        schema_to_select=FilterRead,
        return_as_model=True
    )
    return patched_filter