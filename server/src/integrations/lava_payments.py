import httpx
import logging

from typing import Any

from ..core.config import settings
from ..models.lava import ProductSchema

from ..models.subscription import SubscriptionRead

from ..core.exceptions.http_exceptions import HTTPException

logger = logging.getLogger(__name__)

API_V2_PRODUCTS_URL = settings.LAVA_API_URL+"/v2/products?feedVisibility=ALL"
API_V3_INVOICE_URL = settings.LAVA_API_URL+"/v3/invoice"

async def get_my_products() -> list[ProductSchema]:
    headers = {"X-Api-Key": settings.LAVA_API_KEY}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url=API_V2_PRODUCTS_URL,
                headers=headers,
                timeout=10.0
            )
            if response.status_code not in [200, 201]:
                error_msg = f"Lava.top returned unexpected status: {response.status_code}"

                logger.error(error_msg)
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )

            data: dict = response.json()
            product_schemas: list[ProductSchema] = []

            if data:
                data_items: list[dict] = data.get("items", [])

                for product in data_items:
                    offers = product.get("offers")
                    if not offers:
                        continue

                    product_title = product.get("title")
                    if "/ seafi" not in product_title:
                        continue

                    include_offer: dict = offers[0]
                    product_schema = ProductSchema(
                        id=product.get("id"),
                        title=product_title,
                        description=product.get("description"),
                        offer_id=include_offer.get("id"),
                        offer_name=include_offer.get("name"),
                        offer_description=include_offer.get("description")
                    )
                    product_schemas.append(product_schema)

                return product_schemas
                
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Products not found"
                )
            
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

async def create_payment_link(telegram_id: int, subscription: SubscriptionRead):
    payload_schema = {
        "email": f"user_{telegram_id}@xaris.tech",
        "offerId": subscription.offer_id,
        "currency": "USD",
        "amount": subscription.amount,
        "successful_return_url": f"{settings.REDIRECT_URL}",
        "failure_return_url": f"{settings.REDIRECT_URL}/failure",
        "cancel_return_url": f"{settings.REDIRECT_URL}/cancel"
    }
    payload_headers = {
        "Accept": "application/json",
        "X-Api_key": settings.LAVA_API_KEY,
        "Content-Type": "application/json"
    }
    payment_timeout_s = 15 * 60
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=API_V3_INVOICE_URL,
                json=payload_schema,
                headers=payload_headers,
                timeout=10.0
            )
            if response.status_code not in [200, 201]:
                error_msg = f"Lava.top returned unexpected status: {response.status_code}"

                logger.error(error_msg)
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )
            invoice = response.json()
            invoice["payment_timeout_s"] = payment_timeout_s

            return invoice

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

from ..api.models import WebhookEventPayment, WebhookEventRefund

async def handle_webhook(webhook: WebhookEventPayment | WebhookEventRefund):
    webhook.event_type