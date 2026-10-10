import httpx
import logging

from typing import Literal
from pydantic import ValidationError

from ...core.exceptions.http_exceptions import (
    HTTPException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
)

from ...core.config import settings
from ...models.subscription_plans import SubscriptionPlanRead

from .models import InvoiceSchema, InvoiceStatus

logger = logging.getLogger("integrations.lava.invoice")

async def async_client(
    method: Literal["GET", "POST"],
    timeout: float = 20.0,
    **kwargs
) -> dict:
    async with httpx.AsyncClient() as aclient:
        try:
            response = await aclient.request(
                method=method,
                **kwargs,
                timeout=timeout
            )
            if response.status_code in (200, 201):
                return response.json()

            try: error = response.json()
            except ValueError: error = {}

            if not isinstance(error, dict):
                error = {}

            lava_error = f"{error.get('error')} | {error.get('details')}"
            logger.error(
                "Payment provider return error: %s | %s",
                response.status_code,
                lava_error
            )

            if response.status_code == 400:
                raise BadRequestException(lava_error)
            if response.status_code == 401:
                raise UnauthorizedException(lava_error)
            if response.status_code == 403:
                raise ForbiddenException(lava_error)
            if response.status_code == 404:
                raise NotFoundException(lava_error)

            raise HTTPException(status_code=502, detail=lava_error)

        except httpx.TimeoutException:
            error_msg = "Response timeout error"
            logger.exception(error_msg, exc_info=True)
            raise HTTPException(status_code=504, detail=error_msg)

        except httpx.RequestError:
            error_msg = "Bad Request"
            logger.exception(error_msg, exc_info=True)
            raise HTTPException(status_code=502, detail=error_msg)

        except (
            HTTPException,
            BadRequestException,
            UnauthorizedException,
            ForbiddenException,
            NotFoundException
        ): raise

        except Exception:
            error_msg = "Unexpected exception"
            logger.exception(error_msg, exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)

async def create_invoice_link(
    telegram_id: int,
    plan: SubscriptionPlanRead,
    currency: Literal["USD", "RUB"]
) -> InvoiceSchema:
    amount = plan.amount_usd if currency == "USD" else plan.amount_usd * 85
    
    payload = {
        "email": f"user_{telegram_id}@xaris.tech",
        "offerId": plan.offer_id,
        "currency": currency,
        "amount": amount,
        "successful_return_url": f"{settings.LAVA_REDIRECT_URI}/success",
        "failure_return_url": f"{settings.LAVA_REDIRECT_URI}/failure",
        "cancel_return_url": f"{settings.LAVA_REDIRECT_URI}/cancel"
    }
    headers = {
        "Accept": "application/json",
        "X-Api-Key": settings.LAVA_API_KEY,
        "Content-Type": "application/json"
    }

    data = await async_client(
        method='POST',
        url=f"{settings.LAVA_API_URL}/v3/invoice",
        headers=headers,
        json=payload
    )
    data["payment_timeout_s"] = 15 * 60
    
    try:
        return InvoiceSchema(**data)
    
    except ValidationError as exc:
        logger.exception("Invalid Lava invoice response")
        raise HTTPException(
            status_code=502,
            detail="Invalid response from payment provider"
        ) from exc

async def check_invoice_status(invoice_id: str) -> InvoiceStatus:
    headers = {
        "Accept": "application/json",
        "X-Api-Key": settings.LAVA_API_KEY,
        "Content-Type": "application/json"
    }

    data = await async_client(
        method='GET',
        url=f"{settings.LAVA_API_URL}/v1/invoices/{invoice_id}",
        headers=headers
    )

    try:
        invoice_status = InvoiceStatus(**data)
        invoice_status.status = invoice_status.status.lower()
        if invoice_status.status == "completed":
            invoice_status.status == "success"
            
        return invoice_status
    
    except ValidationError as exc:
        logger.exception("Invalid Lava invoice response")
        raise HTTPException(
            status_code=502,
            detail="Invalid response from payment provider"
        ) from exc