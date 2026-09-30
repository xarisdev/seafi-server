from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from ...core.exceptions.http_exceptions import NotFoundException

from ...db.database import get_db
from ...crud.crud_plans import crud_plans

from ...models.subscription_plans import SubscriptionPlanCreate, SubscriptionPlanRead, SubscriptionPlanUpdate

router = APIRouter(prefix="/plans", tags=["Subscription Plans"])

@router.post("", response_model=SubscriptionPlanRead, status_code=201)
async def create_plan(
    plan: SubscriptionPlanCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    created_plan = await crud_plans.create(
        db=db,
        object=plan,
        return_as_model=True,
        schema_to_select=SubscriptionPlanRead
    )

    return created_plan

# TODO

@router.get("", response_model=list[SubscriptionPlanRead])
async def get_plans(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    data = await crud_plans.get_multi(db=db, schema_to_select=SubscriptionPlanRead)
    plans = data.get("data", [])
    if not plans:
        raise NotFoundException("Subscription plans list is empty.")

    return plans

@router.get("/{subscription_plan_id}", response_model=SubscriptionPlanRead)
async def get_plan(
    subscription_plan_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    plan = await crud_plans.get(
        db=db,
        schema_to_select=SubscriptionPlanRead,
        return_as_model=True,
        one_or_none=True,
        id=subscription_plan_id
    )
    if not plan:
        raise NotFoundException("Subscription plan not found")
    
    return plan

@router.patch("/{subscription_plan_id}", response_model=SubscriptionPlanRead, status_code=202)
async def patch_plan(
    subscription_plan_id: int,
    subscription_plan_data: SubscriptionPlanUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    db_sub = await crud_plans.exists(db=db, id=subscription_plan_id)
    if not db_sub:
        raise NotFoundException(f"Subscription '{subscription_plan_id}' not found")
    
    updated_subscription_plan = await crud_plans.update(
        db=db,
        object=subscription_plan_data,
        schema_to_select=SubscriptionPlanUpdate,
        return_as_model=True,
        id=subscription_plan_id
    )
    return updated_subscription_plan