from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, Depends
from ...core.exceptions.http_exceptions import (
    NotFoundException,
    DuplicateValueException
)

from ...db.database import get_db
from ...crud.crud_plans import crud_plans
from ...models.plan import PlanCreate, PlanRead, PlanUpdate

router = APIRouter(prefix="/plans", tags=["Subscription Plans"])

@router.post("", response_model=PlanRead, status_code=201)
async def create_plan(
    plan: PlanCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PlanRead:
    try:
        created_plan = await crud_plans.create(
            db=db,
            object=plan,
            return_as_model=True,
            schema_to_select=PlanRead
        )
    except IntegrityError:
        raise DuplicateValueException("Integrity Error")

    return created_plan

@router.get("", response_model=list[PlanRead])
async def get_plans(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[PlanRead]:
    data = await crud_plans.get_multi(
        db=db,
        schema_to_select=PlanRead
    )
    
    plans = data.get("data", [])
    return plans

@router.get("/{plan_id}", response_model=PlanRead)
async def get_plan(
    plan_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PlanRead:
    plan = await crud_plans.get(
        db=db,
        id=plan_id,
        schema_to_select=PlanRead,
        return_as_model=True,
        one_or_none=True
    )
    if not plan:
        raise NotFoundException(f"Plan: {plan_id} not found")
    
    return plan

@router.patch("/{plan_id}", response_model=PlanRead, status_code=202)
async def patch_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PlanRead:
    updated_plan = await crud_plans.update(
        db=db,
        id=plan_id,
        object=plan_data,
        schema_to_select=PlanRead,
        return_as_model=True,
        one_or_none=True
    )
    if updated_plan is None:
        raise NotFoundException(f"Plan: {plan_id} not found")
    
    return updated_plan