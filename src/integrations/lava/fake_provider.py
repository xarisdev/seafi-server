from decimal import Decimal

from ...enums.invoice import EnumInvoiceCurrency, EnumInvoiceStatus
from ...models.invoice import InvoiceCreate
from .models import ProductSchema


def build_fake_products() -> list[ProductSchema]:
    return [
        ProductSchema(
            id="fake-product-1",
            title="/ seafi test premium",
            description="Test product used in local and CI runs.",
            offer_id="FAKE-OFFER-ID",
            offer_name="test-premium",
            offer_description="Monthly premium subscription",
        )
    ]


def build_fake_invoice(
    *,
    user_id: int,
    plan_id: int,
    offer_id: str,
    telegram_id: int,
    amount: Decimal,
    currency: EnumInvoiceCurrency,
) -> InvoiceCreate:
    return InvoiceCreate(
        user_id=user_id,
        plan_id=plan_id,
        contract_id=f"fake-contract-{telegram_id}-{plan_id}-{offer_id}",
        payment_url=f"https://example.test/pay/{telegram_id}/{plan_id}",
        currency=currency,
        amount_total=amount,
        status=EnumInvoiceStatus.PENDING,
    )
