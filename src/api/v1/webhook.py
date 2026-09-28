import logging

from fastapi import APIRouter, Request, Depends
from ..dependencies import verify_lava_webhook_key

from ...models.webhook import WebhookEventPayment, WebhookEventRefund

from ...integrations.lava_payments import handle_webhook

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Webhook"], dependencies=[Depends(verify_lava_webhook_key)])

@router.post("/webhook", status_code=200)
async def receive_webhook(request: Request):
    event_type = request.get("eventType")
    event, _type = event_type.split(".")
    webhook_schema = {
        "payment": WebhookEventPayment,
        "refund": WebhookEventRefund
    }.get(event)

    if not webhook_schema:
        error_msg = f"Unexpected webhook eventType: {event_type}"
        logger.error(error_msg)
        return

    webhook = webhook_schema(**request)
    await handle_webhook(webhook)