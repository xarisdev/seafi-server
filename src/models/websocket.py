from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..enums.invoice import EnumInvoiceStatus
from .advertisement import AdvertisementRead

class WebSocketMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    buyer_email: str
    contract_id: str
    invoice_status: EnumInvoiceStatus

    created_at: datetime


class AdvertisementDeliveryMessage(BaseModel):
    type: Literal["advertisement"] = "advertisement"
    delivery_id: int
    telegram_id: int
    advertisement: AdvertisementRead


class AdvertisementDeliveryAck(BaseModel):
    telegram_id: int
    success: bool
    error: str | None = None


class AdminAlertMessage(BaseModel):
    type: Literal["admin_alert"] = "admin_alert"
    telegram_id: int
    source: str
    message: str
    created_at: datetime