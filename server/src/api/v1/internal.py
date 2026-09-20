from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, HTTPException, Depends

from ...db.database import get_db
from ...crud.crud_users import crud_users
from ...crud.crud_filters import crud_filters
from ...models.filter import FilterRead

router = APIRouter(prefix="/internal", tags=["Internal"])

@router.get("/task/{filter_id}", response_model=FilterRead)
async def get_task(
    filter_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    target_filter = await crud_filters.get(db=db, id=filter_id)
    if not target_filter or target_filter.price_min == -1:
        raise HTTPException(
            status_code=204,
            detail="Filter is not configured"
        )

    user = await crud_users.get(db=db, telegram_id=target_filter.telegram_id)
    if not user or not user.is_premium:
        raise HTTPException(
            status_code=402,
            detail="Payment Required"
        )

    return target_filter