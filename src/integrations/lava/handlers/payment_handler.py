from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from ....services.payment import failed_invoice_payment
from ....services.subscription import activate_user_subscription

async def payment_handler(
    db: AsyncSession,
    event_status,
    contract_id,
    invoice_status,
    source,
):
    if event_status == "success":
        await activate_user_subscription(
            db=db,
            contract_id=contract_id,
            invoice_status=invoice_status,
            source=source
        )

    elif event_status == "failed":
        await failed_invoice_payment(
            db=db,
            contract_id=contract_id,
            invoice_status=invoice_status
        )

    else:
        raise ValueError

async def refund_or_chargeback_handler(
    db: AsyncSession,
    event_status,
    contract_id,
    invoice_status,
    source
):
    if event_status == "":
        pass

    elif event_status == "":
        pass

    else:
        raise ValueError