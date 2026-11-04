from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_promocodes import crud_promocodes
from ...db.database import get_db
from ...models.promocode import PromocodeCreate, PromocodeRead
from ...models.promouse import PromouseCreate
from ...models.subscription import SubscriptionRead
from ...services.promocode import apply_promocode, get_promocode_by_code
from ...models.user import User
from ..dependencies import user_by_query

router = APIRouter(prefix="/promocodes", tags=["Promocodes"])


@router.post("", response_model=PromocodeRead, status_code=201)
async def create_promocode(
    payload: PromocodeCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PromocodeRead:
    normalized_code = payload.code.strip().upper()
    if await crud_promocodes.exists(db=db, code=normalized_code):
        raise DuplicateValueException("Promocode already exists")

    promocode = await crud_promocodes.create(
        db=db,
        object=PromocodeCreate(
            code=normalized_code,
            plan_id=payload.plan_id,
            duration_hours=payload.duration_hours,
            usage_limit=payload.usage_limit,
            expires_at=payload.expires_at,
        ),
        schema_to_select=PromocodeRead,
        return_as_model=True,
    )
    return promocode


@router.get("", response_model=list[PromocodeRead])
async def list_promocodes(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[PromocodeRead]:
    result = await crud_promocodes.get_multi(
        db=db,
        schema_to_select=PromocodeRead,
    )
    return result.get("data", [])


@router.get("/{code}", response_model=PromocodeRead)
async def get_promocode(
    code: str,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PromocodeRead:
    promocode = await get_promocode_by_code(db, code)
    if promocode is None:
        raise NotFoundException(f"Promocode '{code}' not found")
    return promocode


@router.post("/{code}/activate", response_model=SubscriptionRead)
async def activate_promocode(
    code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(user_by_query)],
) -> SubscriptionRead:
    subscription = await apply_promocode(db=db, user_id=user.id, code_value=code)
    return SubscriptionRead(
        id=subscription.id,
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        invoice_id=subscription.invoice_id,
        created_at=subscription.created_at,
        started_at=subscription.started_at,
        expires_at=subscription.expires_at,
        source=subscription.source,
    )
