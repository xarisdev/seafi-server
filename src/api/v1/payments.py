from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Query
from ...core.exceptions.http_exceptions import (
    BadRequestException,
    NotFoundException
)

from ..dependencies import get_user_by_query

from ...db.database import get_db
from ...crud.crud_plans import crud_plans
from ...crud.crud_invoices import crud_invoices
from ...models.user import User
from ...models.plan import PlanRead
from ...models.invoice import InvoiceRead, EnumInvoiceCurrency, EnumInvoiceStatus

from ...services.subscription import check_active_subscription
from ...services.payment import check_pending_invoice, get_user_invoices, cancel_user_invoice

from ...integrations.lava.invoice import create_lava_invoice, check_lava_invoice
from ...integrations.lava.handlers.payment_handler import payment_handler

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/invoices", response_model=InvoiceRead, status_code=201)
async def create_invoice(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_user_by_query)],
    plan_id: Annotated[int, Query(alias="plan_id")],
    currency: Annotated[
        EnumInvoiceCurrency,
        Query(alias="currency")
    ] = EnumInvoiceCurrency.USD
) -> InvoiceRead:

    # ------------ Plan info ------------

    plan = await crud_plans.get(
        db=db,
        id=plan_id,
        schema_to_select=PlanRead,
        return_as_model=True,
        one_or_none=True
    )
    if plan is None:
        raise NotFoundException("Subscription plan not found")
    
    # ------------ Check conflicts ------------

    if await check_active_subscription(db=db, user_id=user.id):
        raise BadRequestException("User already has an active subscription")

    if await check_pending_invoice(db=db, user_id=user.id):
        raise BadRequestException("User has an incomplete invoice")

    # ------------ Create invoice ------------

    invoice_schema = await create_lava_invoice(
        user_id=user.id,
        plan_id=plan.id,
        offer_id=plan.offer_id,
        amount=plan.amount,
        currency=currency
    )
    created_invoice = await crud_invoices.create(
        db=db,
        object=invoice_schema,
        schema_to_select=InvoiceRead,
        return_as_model=True
    )

    return created_invoice

@router.get("/invoices", response_model=list[InvoiceRead])
async def get_user_invoices_by_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_user_by_query)],
    status: Annotated[EnumInvoiceStatus | None, Query(alias="status")] = None
) -> list[InvoiceRead]:
    result = await get_user_invoices(db=db, user_id=user.id, status=status)
    return result

@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
async def check_invoice(
    db: Annotated[AsyncSession, Depends(get_db)],
    invoice_id: int
) -> InvoiceRead:
    invoice = await crud_invoices.get(
        db=db,
        id=invoice_id,
        schema_to_select=InvoiceRead,
        return_as_model=True,
        one_or_none=True
    )
    if invoice is None:
        raise NotFoundException("Invoice not found")

    _status = await check_lava_invoice(invoice=invoice)
    if _status is not None:
        await payment_handler(
            db=db,
            event_status=_status[1],
            contract_id=invoice.contract_id,
            invoice_status=_status[0],
            source='lava'
        )
        invoice = await crud_invoices.get(
            db=db,
            id=invoice_id,
            schema_to_select=InvoiceRead,
            return_as_model=True,
            one_or_none=True
        )

    return invoice

@router.post("/invoices/{invoice_id}/cancel", status_code=204)
async def cancel_invoice(
    db: Annotated[AsyncSession, Depends(get_db)],
    invoice_id: int
):
    await cancel_user_invoice(db=db, invoice_id=invoice_id)
    return

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