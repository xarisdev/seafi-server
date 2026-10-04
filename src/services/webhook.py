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
    webhook = WebhookCreate(event_id=data["event_id"], datetime=data["timestamp"])
    
    if await crud_webhooks.exists(db=db, event_id=webhook.event_id):
        logger.info(f"Webhook already exists: {webhook.event_id}")
        return "exists"
    
    try:
        await crud_webhooks.create(
            db=db,
            object=webhook
        )
        logger.info(f"Webhook {webhook.event_id} created.")
        return "created"
    
    except IntegrityError:
        await db.rollback()
        return "exists"