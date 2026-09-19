from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from ..dependencies import verify_secret_key

from ..models import CreatePaymentLinkSchema
from ...core.config import settings

from ...integrations.lava_payments import get_my_products, generate_payment_link

router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(verify_secret_key)])

@router.get("/products")
async def get_products(telegram_id: Annotated[Optional[int], Query(description="Administrator ID")] = None):
    if telegram_id != settings.ADMIN_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    products = await get_my_products()
    if products:
        return products
    
    return {"status": "error", "msg": "No data received"}

@router.post("/create-link")
async def create_link(
    request: CreatePaymentLinkSchema,
    offerId: Annotated[str, Query(description="Lava.top OfferId")],
    amount: Annotated[float, Query(description="Lava.top offer amount in USD")]
    ):
    response = await generate_payment_link(
        telegram_id=request.telegram_id,
        offerId=offerId,
        amount=amount
    )
    return response

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