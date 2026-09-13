from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..models import CreatePaymentLinkSchema
from ...app.config import settings
from ...crud.lava_service import get_my_products, generate_payment_link

from ..dependencies import verify_secret_key

router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(verify_secret_key)])

@router.get("/products")
async def get_products(telegram_id: Annotated[Optional[int], Query(description="Administator ID")] = None):
    if telegram_id != settings.ADMIN_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    result = await get_my_products()
    if result:
        return result
    
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