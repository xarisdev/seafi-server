from typing import Annotated

from fastapi import APIRouter, Depends

from ..dependencies import verify_x_admin_key

from ...integrations.lava_payments import get_my_products

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(verify_x_admin_key)]
)

@router.get("")
async def get_products():
    products = await get_my_products()
    if products: return products
    
    return {"status": "error", "msg": "No data received"}

@router.post("")
async def update_products():
    products = await get_my_products()
    if not products:
        return {
            "status": "error",
            "msg": "No data received"
        }