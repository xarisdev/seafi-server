from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from ...db.database import get_db

from fastapi import APIRouter, Depends, Query
from ...core.exceptions.http_exceptions import NotFoundException

from ..models import PaymentLinkSchema

from ...models.subscription import SubscriptionRead

from ...crud.crud_subscriptions import crud_subscriptions

from ...integrations.lava_payments import create_payment_link

router = APIRouter(prefix="/payments", tags=["Payments"])

# link
# payment timeout

@router.post("/create-link/{subscription_id}", response_model=PaymentLinkSchema)
async def create_link(
    subscription_id: int,
    telegram_id: Annotated[int, Query(alias="telegram_id")],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    subscription = await crud_subscriptions.get(
        db=db,
        schema_to_select=SubscriptionRead,
        return_as_model=True,
        one_or_none=True,
        id=subscription_id
    )
    if subscription is None:
        raise NotFoundException("Subscription not found")

    payment_data = await create_payment_link(telegram_id, subscription)
    schema = PaymentLinkSchema(**payment_data)

    return schema

# redirects временные шаблоны

@router.get("/success")
async def payment_success(
    invoiceId: Annotated[int, Query(description="Offer invoice id")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoiceId": invoiceId}

@router.get("/failure")
async def payment_failure(
    invoiceId: Annotated[int, Query(description="Offer invoice id")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoiceId": invoiceId}

@router.get("/cancel")
async def payment_cancel(
    invoiceId: Annotated[int, Query(description="Offer invoice id")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoiceId": invoiceId}