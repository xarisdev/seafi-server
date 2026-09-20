from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from ..dependencies import verify_admin_key
from ...core.exceptions.http_exceptions import NotFoundException

from ...db.database import get_db
from ...crud.crud_subscriptions import crud_subscriptions

from ...models.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionRead

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/", response_model=SubscriptionRead, status_code=201)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_auth: Annotated[str, Depends(verify_admin_key)]
):
    created_subscription = await crud_subscriptions.create(db=db, object=subscription, return_as_model=SubscriptionRead)

    return created_subscription

@router.get("/", response_model=list[SubscriptionRead])
async def get_subscriptions(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    data = await crud_subscriptions.get_multi(db=db, schema_to_select=SubscriptionRead)
    subscriptions = data.get("data", [])
    if not subscriptions:
        raise NotFoundException("Subscriptions list is empty.")

    return subscriptions

@router.patch("/{subscription_id}", response_model=SubscriptionRead, status_code=202)
async def patch_subscription(
    subscription_id: int,
    subscription_data: SubscriptionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_auth: Annotated[str, Depends(verify_admin_key)]
):
    db_sub = await crud_subscriptions.exists(db=db, id=subscription_id)
    if not db_sub:
        raise NotFoundException(f"Subscription '{subscription_id}' not found")
    
    updated_subscription = await crud_subscriptions.update(
        db=db,
        object=subscription_data,
        id=subscription_id
    )
    return updated_subscription