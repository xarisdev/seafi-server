import httpx

from typing import Any

from ..app.config import settings
from ..models.lava import ProductSchema

API_V2_PRODUCTS_URL = settings.LAVA_API_URL+"/v2/products?feedVisibility=ALL"
API_V3_INVOICE_URL = settings.LAVA_API_URL+"/v3/invoice"

SEAFI_PAYMENTS_URL = "https://seafi.xaris.space/payments/redirect"

async def get_my_products() -> dict[str, Any]:
    headers = {"X-Api-Key": settings.LAVA_API_KEY}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url=API_V2_PRODUCTS_URL,
                headers=headers,
                timeout=10.0
            )
            if response.status_code not in [200, 201]:
                return {"status": "failed", "msg": "GET products error"}

            data = response.json()
            if data:
                products: list[ProductSchema] = []
                items: list[dict] = data.get("items", [])

                for product in items:
                    offers = product.get("offers")
                    if not offers:
                        continue

                    include_offer = offers[0]
                    schema = ProductSchema(
                        **product,
                        offer_id=include_offer.get("id"),
                        offer_name=include_offer.get("name")
                    )
                    if "/ seafi" in schema.title:
                        products.append(schema)

                result = {
                    "status": "success",
                    "products": [schema.model_dump() for schema in products]
                }
                return result
        except httpx.RequestError:
            return {"status": "failed", "msg": "Network error"}
        except:
            raise


async def generate_payment_link(
    telegram_id: int,
    offerId: str,
    amount: float,
    currency: str = "USD",
    successful_return_url: str = f"{SEAFI_PAYMENTS_URL}/success",
    failure_return_url: str = f"{SEAFI_PAYMENTS_URL}/failure",
    cancel_return_url: str = f"{SEAFI_PAYMENTS_URL}/cancel"
) -> dict[str, str]:
    payload_schema = {
        "email": f"user_{telegram_id}@xaris.tech",
        "offerId": offerId,
        "currency": currency,
        "amount": amount,
        "successful_return_url": successful_return_url,
        "failure_return_url": failure_return_url,
        "cancel_return_url": cancel_return_url
    }
    payload_headers = {
        "Accept": "application/json",
        "X-Api-Key": settings.LAVA_API_KEY,
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=API_V3_INVOICE_URL,
                json=payload_schema,
                headers=payload_headers,
                timeout=10.0
            )
            if response.status_code not in [200, 201]:
                return {"status": "failed", "msg": response.text}

            invoice = response.json()
            return {
                "status": "success",
                "invoice": invoice
            }
        except httpx.RequestError as exc:
            return {"status": "failed", "msg": "Network error"}