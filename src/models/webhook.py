from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from datetime import datetime

class Webhook(Base):
    __tablename__ = "webhooks"

    contractId: Mapped[str] = mapped_column(primary_key=True)
    datetime: Mapped[datetime] = mapped_column(DateTime)

class WebhookCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    contractId: str
    datetime: datetime

class WebhookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractId: str
    datetime: datetime