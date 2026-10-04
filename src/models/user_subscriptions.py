from sqlalchemy import Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, foreign

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from typing import Optional
from datetime import datetime, timezone

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscription_plans.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    status: Mapped[str] = mapped_column(String(255))

class UserSubscriptionCreate(BaseModel):
    invoice_id: str

    user_id: int
    plan_id: int

    status: str

class UserSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    invoice_id: str
    
    user_id: int
    plan_id: int

    created_at: datetime
    started_at: datetime | None
    expires_at: datetime | None

    status: str

class UserSubscriptionUpdate(BaseModel):
    started_at: datetime | None
    expires_at: datetime | None
    
    status: str