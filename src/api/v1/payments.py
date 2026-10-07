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
from ...models.user_subscriptions import UserSubscriptionCreate, UserSubscriptionRead
from ...integrations.lava.models import InvoiceSchema
from ...integrations.lava.invoice import create_invoice_link
from ...services.subscription import get_actual_subscription

from ..models import CreateLinkResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-link/{plan_id}", response_model=CreateLinkResponse, status_code=201)
async def create_link(
    plan_id: int,
    user: Annotated[User, Depends(get_user_by_query)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> CreateLinkResponse:

    started_at = None
    expires_at = None

    # ------------ Check active ------------

    result = await get_actual_subscription(db=db, user_id=user.id)
    if result is not None:
        started_at = result.expires_at

    # ------------ Plan info ------------

    plan = await crud_plans.get(
        db=db,
        schema_to_select=SubscriptionPlanRead,
        return_as_model=True,
        one_or_none=True,
        id=plan_id
    )
    if plan is None:
        raise NotFoundException("Subscription plan not found")

    # ------------ Create invoice&sub ------------

    invoice_schema = await create_invoice_link(user.telegram_id, plan)

    subscription = await crud_subscriptions.create(
        db=db,
        object=UserSubscriptionCreate(
            invoice_id=invoice_schema.id,
            user_id=user.id,
            plan_id=plan.id,
            started_at=started_at,
            expires_at=expires_at,
            status=invoice_schema.status,
        ),
        schema_to_select=UserSubscriptionRead,
        return_as_model=True
    )

    return CreateLinkResponse(
        invoice=invoice_schema,
        subscription=subscription
    )

# ------------ redirect placeholders ------------

@router.get("/redirect/success")
async def payment_success(
    invoice_id: Annotated[str, Query(alias="invoiceId", description="OfferId / invoiceId / ContractId")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoice_id": invoice_id}

@router.get("/redirect/failure")
async def payment_failure(
    invoice_id: Annotated[str, Query(alias="invoiceId", description="OfferId / invoiceId / ContractId")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoice_id": invoice_id}

@router.get("/redirect/cancel")
async def payment_cancel(
    invoice_id: Annotated[str, Query(alias="invoiceId", description="OfferId / invoiceId / ContractId")],
    status: Annotated[str, Query(description="Payment status")]
) -> dict:
    return {"status": status, "invoice_id": invoice_id}