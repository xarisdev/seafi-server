from datetime import datetime, timedelta, UTC

from fastapi import HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions.http_exceptions import BadRequestException, NotFoundException
from ..crud.crud_promouses import crud_promouses
from ..models.plan import Plan
from ..models.promocode import Promocode
from ..models.promouse import Promouse, PromouseCreate
from ..models.subscription import Subscription
from .payment import check_pending_invoice
from .subscription import get_active_user_subscription


async def get_promocode_by_code(db: AsyncSession, code: str) -> Promocode | None:
    normalized_code = code.strip().upper()
    return await db.scalar(
        select(Promocode).where(Promocode.code == normalized_code)
    )


async def is_promocode_expired(code: Promocode) -> bool:
    if code.expires_at is None:
        return False
    return datetime.now(UTC) > code.expires_at


async def _count_promocode_uses(db: AsyncSession, code_id: int) -> int:
    result = await db.scalar(
        select(func.count(Promouse.id)).where(Promouse.code_id == code_id)
    )
    return int(result or 0)


async def validate_promocode_for_user(db: AsyncSession, code: Promocode, user_id: int) -> None:
    if await is_promocode_expired(code):
        raise BadRequestException("Promocode expired")

    if code.usage_limit is not None:
        used = await _count_promocode_uses(db, code.id)
        if used >= code.usage_limit:
            raise BadRequestException("Promocode usage limit reached")

    used_by_user = await db.scalar(
        select(Promouse.id).where(
            Promouse.user_id == user_id,
            Promouse.code_id == code.id,
        )
    )
    if used_by_user is not None:
        raise HTTPException(status_code=409, detail="Promocode already used by this user")


async def apply_promocode(db: AsyncSession, user_id: int, code_value: str) -> Subscription:
    code = await get_promocode_by_code(db, code_value)
    if code is None:
        raise NotFoundException(f"Promocode '{code_value}' not found")

    await validate_promocode_for_user(db, code, user_id)

    if await check_pending_invoice(db=db, user_id=user_id):
        raise BadRequestException("User has an incomplete invoice")

    active_subscription = await get_active_user_subscription(db, user_id=user_id)
    if active_subscription is not None:
        extension_hours = code.duration_hours or 24
        base_expiry = active_subscription.expires_at or datetime.now(UTC)
        new_expiry = base_expiry + timedelta(hours=extension_hours)

        await db.execute(
            update(Subscription)
            .where(Subscription.id == active_subscription.id)
            .values(expires_at=new_expiry)
        )

        await crud_promouses.create(
            db=db,
            object=PromouseCreate(
                user_id=user_id,
                code_id=code.id,
            ),
            return_as_model=False,
        )
        return active_subscription

    if code.plan_id is None:
        raise BadRequestException("This promocode requires an active subscription or a target plan")

    plan = await db.scalar(
        select(Plan).where(Plan.id == code.plan_id)
    )
    if plan is None:
        raise NotFoundException(f"Plan '{code.plan_id}' not found")

    started_at = datetime.now(UTC)
    duration_hours = code.duration_hours or plan.duration
    expires_at = started_at + timedelta(hours=duration_hours)

    subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        invoice_id=None,
        created_at=started_at,
        started_at=started_at,
        expires_at=expires_at,
        source=f"promo:{code.code}"
    )
    db.add(subscription)
    await db.flush()

    await crud_promouses.create(
        db=db,
        object=PromouseCreate(
            user_id=user_id,
            code_id=code.id,
        ),
        return_as_model=False,
    )

    return subscription
