import httpx
import logging

from ...core.exceptions.http_exceptions import HTTPException

from ...core.config import settings

from .models import ProductSchema

logger = logging.getLogger("integrations.lava.products")

async def get_lava_products() -> list[ProductSchema]:
    headers = {"X-Api-Key": settings.LAVA_API_KEY}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url=f"{settings.LAVA_API_URL}/v2/products?feedVisibility=ALL",
                headers=headers,
                timeout=15.0
            )
            if response.status_code != 200:
                error_msg = f"Lava.top returned unexpected status: {response.status_code}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)

            data: dict = response.json()
            if not data:
                warn_msg = "Products not found"
                logger.warning(warn_msg)
                raise HTTPException(status_code=404, detail=warn_msg)

            products: list[ProductSchema] = []
            items = data.get("items", [])
            
            for product in items:
                offers = product.get("offers")
                if not offers:
                    continue

                title = product.get("title")
                if "/ seafi" not in title:
                    continue

                include_offer = offers[0]

                product_schema = ProductSchema(
                    id=product.get("id"),
                    title=title,
                    description=product.get("description"),
                    offer_id=include_offer.get("id"),
                    offer_name=include_offer.get("name"),
                    offer_description=include_offer.get("description"),
                )
                products.append(product_schema)

            logger.info(f"Found {len(products)} products")
            return products
        
        except httpx.RequestError:
            error_msg = "Bad Request integrated service. (Lava.top)"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=502,
                detail=error_msg
            )

        except httpx.TimeoutException:
            error_msg = "Response timeout error. (Lava.top)"

            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=504,
                detail=error_msg
            )

        except Exception:
            error_msg = "Unexcepted Exception"

            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )