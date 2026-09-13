from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    HTTPException, status,
    Depends
)

from ...db.database import get_db
from ...db.models import User, Subscription, Filter

from ..models import FilterCreateRequest

from ..dependencies import verify_secret_key

router = APIRouter(tags=["filters"], dependencies=[Depends(verify_secret_key)])

@router.post("/filters/new", status_code=status.HTTP_201_CREATED)
async def new_filter(
    request: FilterCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, str]:
    user_result = await db.execute(select(User).where(User.telegram_id == request.telegram_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    sub_result = await db.execute(select(Subscription).where(Subscription.id == user.subscription_id))
    subscription = sub_result.scalar_one_or_none()
    if not subscription or not subscription.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No active subscription")

    if subscription.filter_id:
        filter_result = await db.execute(select(Filter).where(Filter.id == subscription.filter_id))
        existing_filter = filter_result.scalar_one_or_none()

        if existing_filter:
            existing_filter.price_min = request.price_min
            existing_filter.price_max = request.price_max
            existing_filter.owner = request.owner
            await db.flush()
            return {"status": "success"}

    new_filter = Filter(
        price_min=request.price_min,
        price_max=request.price_max,
        owner=request.owner
    )
    db.add(new_filter)
    await db.flush()

    subscription.filter_id = new_filter.id
    await db.flush()

    return {"status": "success"}