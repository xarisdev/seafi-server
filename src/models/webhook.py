from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from datetime import datetime

class Webhook(Base):
    __tablename__ = "webhooks"

    contractId: Mapped[str] = mapped_column(primary_key=True)
    buyer_email: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class WebhookCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    contractId: str
    buyer_email: str
    status: str

    timestamp: datetime

class WebhookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractId: str
    buyer_email: str
    status: str
    timestamp: datetime