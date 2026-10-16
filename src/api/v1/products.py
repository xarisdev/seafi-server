from fastapi import APIRouter
from ...core.exceptions.http_exceptions import (
    NotFoundException
)

from ...integrations.lava.models import ProductSchema
from ...integrations.lava.products import get_products

router = APIRouter(prefix="/lava-products", tags=["Products"])

@router.get("")
async def get_lava_products() -> list[ProductSchema]:
    products = await get_products()
    if not products:
        raise NotFoundException("Products not found")
    return products