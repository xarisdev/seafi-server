from fastapi import APIRouter

from ...integrations.lava.models import ProductSchema
from ...integrations.lava.products import get_lava_products

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("")
async def get_products() -> list[ProductSchema]:
    products = await get_lava_products()
    if products: return products
    
    return {"status": "error", "msg": "No data received"}