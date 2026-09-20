from sqlalchemy import Integer, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel

from typing import Optional

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    offer_id: Mapped[str] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(300))

    amount: Mapped[float] = mapped_column(Float)
    duration_hours: Mapped[int] = mapped_column(Integer)

class SubscriptionCreate(BaseModel):
    offer_id: str
    title: str
    description: str
    amount: float
    duration_hours: int

class SubscriptionUpdate(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    amount: Optional[float]
    duration_hours: Optional[int]

class SubscriptionRead(BaseModel):
    id: int
    offer_id: str
    title: str
    description: str
    amount: float
    duration_hours: int