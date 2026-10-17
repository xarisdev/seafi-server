from datetime import datetime, timedelta, UTC

from sqlalchemy import select, exists, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.invoice import Invoice, EnumInvoiceStatus

async def check_pending_invoice(db: AsyncSession, user_id: int) -> bool:
    return await db.scalar(
        select(
            exists().where(
                Invoice.user_id == user_id,
                Invoice.status == EnumInvoiceStatus.PENDING,
                Invoice.created_at >= datetime.now(UTC) - timedelta(minutes=15)
            )
        )
    )

async def failed_invoice_payment(db: AsyncSession, contract_id: str, invoice_status: EnumInvoiceStatus):
    await db.execute(
        update(Invoice)
        .where(Invoice.contract_id == contract_id)
        .values(status=invoice_status)
    )

async def cancel_invoice(db: AsyncSession, invoice_id: int):
    await db.execute(
        update(Invoice)
        .where(
            Invoice.id == invoice_id,
            Invoice.status == EnumInvoiceStatus.PENDING
        )
        .values(status=EnumInvoiceStatus.CANCELLED)
    )