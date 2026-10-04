import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ...services.webhook import write_webhook
from ...services.subscription import (
    activate_user_subscription,
    failed_user_subscription
)

logger = logging.getLogger("integrations.lava.webhook")

async def handle_webhook(db: AsyncSession, webhook: dict):
    event_id = webhook.get("event_id")
    logger.info(f"Webhook [{event_id}]")

    try:
        event_type: str = webhook.get("eventType")
        event_class, event_status = event_type.split(".")

        if event_class == "payment":
            await payment_handler(
                db=db,
                webhook=webhook,
                event_status=event_status,
            )

        elif event_class == "refund" or event_class == "chargeback":
            await refund_or_chargeback_handler(
                db=db,
                webhook=webhook,
                event_status=event_status
            )

        else:
            logger.warning(f"Unexpected webhook event class")
    
    except Exception:
        logger.error(
            f"Unexpected exception while handling Lava webhook [{event_id}]",
            exc_info=True
        )

async def payment_handler(db: AsyncSession, webhook: dict, event_status: str):
    buyer_email: str = webhook["buyer"]["email"]
    contract_id: str = webhook.get("contract_id")
    logger.info(f"Webhook contract_id: {contract_id}")

    status = await write_webhook(db=db, data=webhook)
    if status == "exists":
        return
    
    if event_status == "success":
        await activate_user_subscription(
            db=db,
            invoice_id=contract_id,
            status=webhook["status"]
        )

    elif event_status == "failed":
        await failed_user_subscription(
            db=db,
            invoice_id=contract_id,
            status=webhook["status"]
        )

    elif event_status == "cancelled": # depricated
        pass

    #await send_notification(
    #    telegram_id=telegram_id,
    #    status=event_status
    #)

async def refund_or_chargeback_handler(db: AsyncSession, event_id: str, event_status: str, webhook: dict):
    pass