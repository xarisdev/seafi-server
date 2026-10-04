import logging

from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.webhook import WebhookCreate
from ..crud.crud_webhooks import crud_webhooks

logger = logging.getLogger("services.webhook")

async def write_webhook(
    db: AsyncSession,
    data: dict
) -> Literal["exists", "created"]:
    webhook = WebhookCreate(contractId=data["contractId"], datetime=data["timestamp"])
    
    if await crud_webhooks.exists(db=db, contractId=webhook.contractId):
        logger.info(f"Webhook already exists: {webhook.contractId}")
        return "exists"
    
    try:
        await crud_webhooks.create(
            db=db,
            object=webhook
        )
        logger.info(f"Webhook {webhook.contractId} created.")
        return "created"
    
    except IntegrityError:
        await db.rollback()
        return "exists"