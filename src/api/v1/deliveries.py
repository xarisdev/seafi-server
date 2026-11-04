from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ...models.websocket import AdvertisementDeliveryAck
from ...services.advertisement_delivery import acknowledge_delivery

router = APIRouter(prefix="/deliveries", tags=["Advertisement deliveries"])


@router.post("/{delivery_id}/ack", status_code=204)
async def acknowledge_advertisement_delivery(
    delivery_id: int,
    payload: AdvertisementDeliveryAck,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await acknowledge_delivery(db, delivery_id, payload)