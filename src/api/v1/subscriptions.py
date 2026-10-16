from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from ...core.exceptions.http_exceptions import (
    NotFoundException
)

from ..dependencies import get_user_by_query

from ...db.database import get_db
from ...models.user import User
from ...models.subscription import (
    Subscription,
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate
)

from ...services.subscription import (
    get_user_subscriptions,
    get_active_user_subscription,
    get_subscription_by_id
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/all", response_model=list[SubscriptionRead])
async def get_all_subscriptions(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_user_by_query)]
) -> list[Subscription]:
    return await get_user_subscriptions(db=db, user_id=user.id)

@router.get("/active", response_model=SubscriptionRead | None)
async def get_active_subscription(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_user_by_query)]
) -> Subscription | None:
    return await get_active_user_subscription(db=db, user_id=user.id)

@router.get("/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription(
    db: Annotated[AsyncSession, Depends(get_db)],
    subscription_id: int
) -> SubscriptionRead:
    subscription = await get_subscription_by_id(db=db, subscription_id=subscription_id)
    
    if subscription is None:
        raise NotFoundException("Subscription not found")
    
    return subscription

# ------------ Manual control (placeholders) ------------

@router.post("/manual/create")
async def manual_post_subscription(
    subscription: SubscriptionCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    pass

@router.patch("/manual/{subscription_id}")
async def manual_patch_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    pass