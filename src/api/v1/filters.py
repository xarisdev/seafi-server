from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from ..dependencies import user_by_query, get_filter_by_path
from ...core.exceptions.http_exceptions import NotFoundException

from ...db.database import get_db
from ...crud.crud_filters import crud_filters
from ...models.filter import FilterCreate, FilterRead, FilterUpdate
from ...models.user import UserRead

router = APIRouter(prefix="/filters", tags=["Filters"])

@router.post("", response_model=FilterRead)
async def create_filter(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserRead, Depends(user_by_query)]
) -> FilterRead:
    created_filter = await crud_filters.create(
        db=db,
        object=FilterCreate(
            user_id=user.id
        ),
        schema_to_select=FilterRead,
        return_as_model=True
    )
    return created_filter

@router.get("/user", response_model=FilterRead)
async def get_filter_by_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserRead, Depends(user_by_query)]
) -> FilterRead:
    db_filter = await crud_filters.get(
        db=db,
        user_id=user.id,
        schema_to_select=FilterRead,
        return_as_model=True,
        one_or_none=True
    )
    
    if db_filter is None:
        raise NotFoundException(f"Filter with user_id '{user.id}' not found")
    
    return db_filter

@router.get("/{id}", response_model=FilterRead)
async def get_filter_by_id(
    db_filter: Annotated[FilterRead, Depends(get_filter_by_path)],
) -> FilterRead:
    return db_filter

@router.patch("/{id}", status_code=204)
async def patch_filter(
    db: Annotated[AsyncSession, Depends(get_db)],
    db_filter: Annotated[FilterRead, Depends(get_filter_by_path)],
    data: FilterUpdate
) -> None:    
    await crud_filters.update(
        db=db,
        id=db_filter.id,
        object=data
    )

@router.post("/{id}/activate", status_code=204)
async def activate_filter(
    db: Annotated[AsyncSession, Depends(get_db)],
    db_filter: Annotated[FilterRead, Depends(get_filter_by_path)]
) -> None:
    pass

@router.post("/{id}/deactivate", status_code=204)
async def deactivate_filter(
    db: Annotated[AsyncSession, Depends(get_db)],
    db_filter: Annotated[FilterRead, Depends(get_filter_by_path)]
) -> None:
    pass