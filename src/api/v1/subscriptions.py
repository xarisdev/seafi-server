from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Query

from ...core.exceptions.http_exceptions import NotFoundException

from ..dependencies import get_user_by_query

from ...db.database import get_db
from ...models.user import User
from ...models.user_subscriptions import UserSubscriptionCreate, UserSubscriptionRead, UserSubscriptionUpdate
from ...crud.crud_subscriptions import crud_subscriptions
from ...services.subscription import get_actual_subscription

from ..models import UserSubscriptionsResponse

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/all", response_model=UserSubscriptionsResponse)
async def get_all_subscriptions(
    user: Annotated[User, Depends(get_user_by_query)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status = Query(alias="status", description="Subscription status", default=None)
) -> UserSubscriptionsResponse:
    result = await crud_subscriptions.get_multi(
        db=db,
        user_id=user.id,
        status=status,
        schema_to_select=UserSubscriptionRead,
        return_as_model=True,
        sort_columns=["id"]
    )
    return result

@router.get("/active", response_model=UserSubscriptionRead | None)
async def get_active_subscription(
    user: Annotated[User, Depends(get_user_by_query)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserSubscriptionRead | None:
    return await get_actual_subscription(db=db, user_id=user.id)

@router.get("/{subscription_id}", response_model=UserSubscriptionRead)
async def get_subscription(
    subscription_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserSubscriptionRead:
    subscription = await crud_subscriptions.get(
        db=db,
        id=subscription_id,
        schema_to_select=UserSubscriptionRead,
        return_as_model=True,
        one_or_none=True
    )
    if subscription is None:
        raise NotFoundException("Subscription not found")
    
    return subscription

# ------------ Manual control (placeholders) ------------

@router.post("/manual/create")
async def manual_post_subscription(
    subscription: UserSubscriptionCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    pass

@router.patch("/manual/{subscription_id}")
async def manual_patch_subscription(
    subscription_id: int,
    subscription: UserSubscriptionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    pass