import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from datetime import datetime, UTC

from ..models.webhook import WebhookCreate
from ..crud.crud_webhooks import crud_webhooks

logger = logging.getLogger("services.webhook")

async def write_webhook(
    db: AsyncSession,
    contract_id: str,
    buyer_email: str,
    invoice_status: str,
    timestamp: str
) -> bool:
    timestamp = datetime.fromisoformat(timestamp).astimezone(UTC)
    webhook = WebhookCreate(
        contractId=contract_id,
        buyer_email=buyer_email,
        status=invoice_status,
        timestamp=timestamp
    )
    
    if await crud_webhooks.exists(db=db, contractId=webhook.contractId):
        logger.info(f"Webhook already exists: {webhook.contractId}")
        return False
    
    try:
        await crud_webhooks.create(db=db, object=webhook)
    
    except IntegrityError:
        await db.rollback()
        logger.info(f"Webhook already exists: {webhook.contractId}")
        return False

    logger.info(f"Webhook {webhook.contractId} created.")
    return True