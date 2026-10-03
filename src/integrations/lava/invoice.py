import httpx
import logging

from ...core.exceptions.http_exceptions import HTTPException

from ...core.config import settings
from ...models.subscription_plans import SubscriptionPlanRead

from .models import InvoiceSchema

logger = logging.getLogger("integrations.lava.invoice")

async def create_invoice_link(
    telegram_id: int,
    plan: SubscriptionPlanRead
) -> InvoiceSchema:
    payload = {
        "email": f"user_{telegram_id}@xaris.tech",
        "offerId": plan.offer_id,
        "currency": "USD",
        "amount": plan.amount_usd,
        "successful_return_url": f"{settings.LAVA_REDIRECT_URI}/success",
        "failure_return_url": f"{settings.LAVA_REDIRECT_URI}/failure",
        "cancel_return_url": f"{settings.LAVA_REDIRECT_URI}/cancel"
    }
    headers = {
        "Accept": "application/json",
        "X-Api-Key": settings.LAVA_API_KEY,
        "Content-Type": "application/json"
    }
    payment_timeout_s = 15 * 60
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=f"{settings.LAVA_API_URL}/v3/invoice",
                headers=headers,
                json=payload,
                timeout=15.0
            )
            if response.status_code not in [200, 201]:
                error_msg = f"Lava.top request status: {response.status_code}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)

            invoice = InvoiceSchema(
                **response.json(),
                payment_timeout_s=payment_timeout_s
            )
            return invoice
        
        except httpx.RequestError:
            error_msg = "Bad Request"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(status_code=502, detail=error_msg)

        except httpx.TimeoutException:
            error_msg = "Response timeout error"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(status_code=504, detail=error_msg)

        except Exception:
            error_msg = "Unexpected exception"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)