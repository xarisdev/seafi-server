from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Query

from ..dependencies import get_user_by_query

from ...core.exceptions.http_exceptions import NotFoundException

from ...db.database import get_db
from ...crud.crud_plans import crud_plans
from ...crud.crud_subscriptions import crud_subscriptions
from ...models.user import User
from ...models.subscription_plans import SubscriptionPlanRead
from ...models.user_subscriptions import UserSubscriptionCreate
from ...integrations.lava.models import InvoiceSchema
from ...integrations.lava.invoice import create_invoice_link

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-link/{plan_id}", status_code=201)
async def create_link(
    plan_id: int,
    user: Annotated[User, Depends(get_user_by_query)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> InvoiceSchema:
    plan = await crud_plans.get(
        db=db,
        schema_to_select=SubscriptionPlanRead,
        return_as_model=True,
        one_or_none=True,
        id=plan_id
    )
    if plan is None:
        raise NotFoundException("Subscription plan not found")

    invoice_schema = await create_invoice_link(user.telegram_id, plan)

    await crud_subscriptions.create(
        db=db,
        object=UserSubscriptionCreate(
            user_id=user.id,
            plan_id=plan.id,
            status=invoice_schema.status,
            invoice_id=invoice_schema.id
        )
    )

    return invoice_schema

# ------------ redirect placeholders ------------

@router.get("/redirect/success")
async def payment_success(
    invoiceId: Annotated[int, Query(description="Offer invoice id")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoiceId": invoiceId}

@router.get("/redirect/failure")
async def payment_failure(
    invoiceId: Annotated[int, Query(description="Offer invoice id")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoiceId": invoiceId}

@router.get("/redirect/cancel")
async def payment_cancel(
    invoiceId: Annotated[int, Query(description="Offer invoice id")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoiceId": invoiceId}