from enum import Enum
from pydantic import BaseModel, ConfigDict

from datetime import datetime

class EventStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class SubscriptionStatus(str, Enum):
    NEW = "new"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    MERGE = "merge"

class SubscriptionRange(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    started_at: datetime | None
    expires_at: datetime | None

class Payload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    invoice_id: str
    event_status: EventStatus
    status: SubscriptionStatus
    timestamp: datetime
    subscription_id: int
    subscription_range: SubscriptionRange