import httpx
import logging

from typing import Literal
from decimal import Decimal, ROUND_HALF_UP
from pydantic import ValidationError

from ...core.exceptions.http_exceptions import (
    HTTPException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
)

from ...core.config import settings
from ...models.invoice import (
    InvoiceCreate,
    InvoiceRead,
    EnumInvoiceCurrency,
    EnumInvoiceCurrencyExchange,
    EnumInvoiceStatus
)

logger = logging.getLogger("integrations.lava.invoice")

# ------------ helpers ------------

def _lava_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "X-Api-Key": settings.LAVA_API_KEY,
        "Content-Type": "application/json"
    }

def _get_amount_by_currency(
    amount: Decimal,
    currency: EnumInvoiceCurrency
) -> Decimal:
    exchange_rate = {
        EnumInvoiceCurrency.RUB: EnumInvoiceCurrencyExchange.RUB,
        EnumInvoiceCurrency.USD: EnumInvoiceCurrencyExchange.USD
    }.get(currency)

    amount = amount * exchange_rate
    final_amount = amount.quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)

    return final_amount

def _normalize_invoice_status(status: str) -> EnumInvoiceStatus:
    return {
        "new": EnumInvoiceStatus.PENDING,
        "in_progress": EnumInvoiceStatus.PENDING,
        "failed": EnumInvoiceStatus.FAILED,
        "cancelled": EnumInvoiceStatus.CANCELLED,
        "success": EnumInvoiceStatus.COMPLETED,
        "completed": EnumInvoiceStatus.COMPLETED
    }[status.lower()]

# ------------ httpx.Client ------------

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

# ------------ API ------------

async def create_lava_invoice(
    user_id: int,
    plan_id: int,
    offer_id: str,
    telegram_id: int,
    amount: Decimal,
    currency: EnumInvoiceCurrency
) -> InvoiceCreate:
    amount = _get_amount_by_currency(amount, currency=currency)

    response = await async_client(
        method='POST',
        url=f"{settings.LAVA_API_URL}/v3/invoice",
        headers=_lava_headers(),
        json={
            "email": f"user_{telegram_id}@xaris.tech",
            "offerId": offer_id,
            "currency": currency,
            "amount": float(amount),
            "successful_return_url": f"{settings.LAVA_REDIRECT_URI}/success",
            "failure_return_url": f"{settings.LAVA_REDIRECT_URI}/failure",
            "cancel_return_url": f"{settings.LAVA_REDIRECT_URI}/cancel"
        }
    )
    response["payment_timeout_s"] = 15 * 60
    
    try:
        return InvoiceCreate(
            user_id=user_id,
            plan_id=plan_id,
            contract_id=response["id"],
            payment_url=response["paymentUrl"],
            currency=response["amountTotal"]["currency"],
            amount_total=response["amountTotal"]["amount"],
            status=_normalize_invoice_status(response["status"])
        )
    
    except ValidationError as exc:
        logger.exception("Invalid Lava invoice response")
        raise HTTPException(
            status_code=502,
            detail="Invalid response from payment provider"
        ) from exc

async def check_lava_invoice(invoice: InvoiceRead) -> tuple[EnumInvoiceStatus, str] | None:
    response = await async_client(
        method='GET',
        url=f"{settings.LAVA_API_URL}/v1/invoices/{invoice.contract_id}",
        headers=_lava_headers()
    )
    invoice_status = _normalize_invoice_status(response["status"])
    
    if invoice.status != invoice_status:
        if invoice_status == EnumInvoiceStatus.PENDING: # ignore
            return None
        
        if invoice_status in (EnumInvoiceStatus.FAILED, EnumInvoiceStatus.CANCELLED):
            if invoice.status == EnumInvoiceStatus.PENDING:
                return [invoice_status, 'failed']
            
        if invoice_status == EnumInvoiceStatus.COMPLETED:
            if any([
                invoice.status == EnumInvoiceStatus.PENDING,
                invoice.status in (EnumInvoiceStatus.FAILED, EnumInvoiceStatus.CANCELLED)
            ]):
                return [invoice_status, 'success']
            
    return None