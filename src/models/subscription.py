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

    amount_usd: Mapped[float] = mapped_column(Float)

    duration_h: Mapped[int] = mapped_column(Integer)

class SubscriptionCreate(BaseModel):
    offer_id: str
    title: str
    description: str

    amount_usd: float

    duration_h: int

class SubscriptionUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    
    amount_usd: Optional[float] = None

    duration_h: Optional[int] = None

class SubscriptionRead(BaseModel):
    id: int
    offer_id: str
    title: str
    description: str
    amount_usd: float
    duration_h: int