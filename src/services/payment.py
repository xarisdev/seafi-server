from datetime import datetime, timedelta, UTC

from sqlalchemy import select, exists, update, case
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

async def get_user_invoices(db: AsyncSession, user_id: int, status: str | None) -> list[Invoice]:
    expires = await db.execute(
        update(Invoice)
        .where(
            Invoice.user_id == user_id,
            Invoice.status == EnumInvoiceStatus.PENDING,
            Invoice.created_at <= datetime.now(UTC) - timedelta(minutes=15)
        )
        .values(status=EnumInvoiceStatus.FAILED)
        .returning(Invoice.id)
    )
    expires_ids = expires.scalars().all()
    
    query = select(Invoice).where(Invoice.user_id == user_id)
    if status:
        query = query.where(Invoice.status == status)

    if expires_ids:
        query = query.where(Invoice.id.not_in(expires_ids))

    result = await db.scalars(query)
    return list(result.all())

async def cancel_user_invoice(db: AsyncSession, invoice_id: int):
    query = (
        update(Invoice)
        .where(
            Invoice.id == invoice_id,
            Invoice.status == EnumInvoiceStatus.PENDING
        )
        .values(
            status=case(
                (
                    Invoice.created_at <= datetime.now(UTC) - timedelta(minutes=15),
                    EnumInvoiceStatus.FAILED
                ),
                else_=EnumInvoiceStatus.CANCELLED
            )
        )
        .returning(Invoice.id, Invoice.status)
    )
    result = await db.execute(query)
    invoice = result.mappings().one_or_none()

    if invoice is None:
        return None

    if invoice["status"] == EnumInvoiceStatus.FAILED:
        return False

    return invoice["id"]