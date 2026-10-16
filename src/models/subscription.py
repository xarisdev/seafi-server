from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone

from ..db.model import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id")
    )
    plan_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("plans.id"),
        nullable=True
    )
    invoice_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("invoices.id"),
        nullable=True,
        unique=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    source: Mapped[str] = mapped_column(String)

class SubscriptionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    
    plan_id: Optional[int] = None
    invoice_id: Optional[int] = None

    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    source: str

class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    plan_id: int | None
    invoice_id: int | None
    created_at: datetime
    started_at: datetime | None
    expires_at: datetime | None
    source: str

class SubscriptionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_id: Optional[int] = None
    invoice_id: Optional[int] = None

    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    source: Optional[str] = None