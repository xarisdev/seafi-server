import logging

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Request, Depends
from ..dependencies import verify_lava_webhook_key

from ...db.database import get_db

from ...integrations.lava.webhook_handler import handle_webhook

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Webhook"], dependencies=[Depends(verify_lava_webhook_key)])

@router.post("/lava", status_code=200)
async def receive_webhook(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        webhook = await request.json()
    except Exception as exc:
        print(exc)
    await handle_webhook(db=db, webhook=webhook)