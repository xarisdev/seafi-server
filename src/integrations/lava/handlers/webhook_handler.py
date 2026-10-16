import logging

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from .payment_handler import payment_handler, refund_or_chargeback_handler
from ..invoice import _normalize_invoice_status

from ....models.websocket import WebSocketMessage
from ....services.webhook import write_webhook
from ....services.websocket import websocket_manager

logger = logging.getLogger("integrations.lava.webhook")

async def handle_webhook(db: AsyncSession, webhook: dict):
    try:
        event_type: str = webhook.get("eventType")
        event_class, event_status = event_type.split(".")

        contract_id: str = webhook["contractId"]
        buyer_email: str = webhook["buyer"]["email"]
        invoice_status = _normalize_invoice_status(webhook["status"])
        timestamp: str = webhook["timestamp"]

        logger.info(f"Webhook [{contract_id}]: {buyer_email} | {event_type} | {invoice_status}")

        # ------------ Save & Check webhook ------------

        if not await write_webhook(
            db=db,
            contract_id=contract_id,
            buyer_email=buyer_email,
            invoice_status=invoice_status,
            timestamp=timestamp
        ):
            return

        # ------------ Payment actions ------------

        if event_class == "payment":
            await payment_handler(
                db=db,
                event_status=event_status,
                contract_id=contract_id,
                invoice_status=invoice_status,
                source="webhook"
            )

        # ------------ User refund (after payment) ------------

        elif event_class in ("refund", "chargeback"):
            await refund_or_chargeback_handler(
                db=db,
                event_status=event_status,
                contract_id=contract_id,
                invoice_status=invoice_status,
                source="webhook"
            )

        else:
            logger.warning(f"Unexpected webhook event class")
    
    except Exception:
        logger.error(
            "Unexpected exception while handling Lava webhook",
            exc_info=True
        )

    await websocket_manager.put_payload(
        WebSocketMessage(
            id=uuid4(),
            buyer_email=buyer_email,
            contract_id=contract_id,
            invoice_status=invoice_status
        )
    )