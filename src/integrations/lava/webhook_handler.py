import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ...services.webhook import write_webhook
from ...services.subscription import (
    activate_user_subscription,
    failed_user_subscription
)
from ...services.websocket import websocket_manager
from ...models.websocket import Payload, SubscriptionRange

logger = logging.getLogger("integrations.lava.webhook")

async def handle_webhook(db: AsyncSession, webhook: dict):
    try:
        event_type: str = webhook.get("eventType")
        event_class, event_status = event_type.split(".")

        contract_id: str = webhook["contractId"]
        buyer_email: str = webhook["buyer"]["email"]
        status: str = webhook["status"]
        timestamp: str = webhook["timestamp"]

        logger.info(f"Webhook [{contract_id}]: {buyer_email} | {event_type} | {status}")

        # ------------ Save webhook ------------

        if not await write_webhook(
            db=db,
            contract_id=contract_id,
            datetime=timestamp
        ):
            return

        # ------------ Payment actions ------------

        if event_class == "payment":
            await payment_handler(
                db=db,
                event_status=event_status,
                buyer_email=buyer_email,
                contract_id=contract_id,
                status=status,
                timestamp=timestamp
            )

        # ------------ User refund (after payment) ------------

        elif event_class in ("refund", "chargeback"):
            await refund_or_chargeback_handler(
                db=db,
                event_status=event_status,
                buyer_email=buyer_email,
                contract_id=contract_id,
                status=status,
                timestamp=timestamp
            )

        else:
            logger.warning(f"Unexpected webhook event class")
    
    except Exception:
        logger.error(
            f"Unexpected exception while handling Lava webhook",
            exc_info=True
        )

async def payment_handler(
    db: AsyncSession,
    event_status: str,
    buyer_email: str,
    contract_id: str,
    status: str,
    timestamp: str
):
    # ------------ Subscription action ------------
    
    if event_status == "success":
        subscription = await activate_user_subscription(
            db=db,
            invoice_id=contract_id,
            status=status
        )

    elif event_status == "failed":
        subscription = await failed_user_subscription(
            db=db,
            invoice_id=contract_id,
            status=status
        )

    else:
        raise ValueError(f"Unexpected event_status: {event_status}")

    # ------------ Send result to bot ------------

    telegram_id = int(buyer_email.split("@")[0].removeprefix("user_"))

    payload = Payload(
        telegram_id=telegram_id,
        invoice_id=subscription.invoice_id,
        event_status=event_status,
        status=subscription.status,
        timestamp=timestamp,
        subscription_id=subscription.id,
        subscription_range=SubscriptionRange(
            created_at=subscription.created_at,
            started_at=subscription.started_at,
            expires_at=subscription.expires_at
        )
    )
    await websocket_manager.send_json(payload=payload)

async def refund_or_chargeback_handler(
    db: AsyncSession,
    event_status: str,
    buyer_email: str,
    contract_id: str,
    status: str,
    timestamp: str
):
    pass