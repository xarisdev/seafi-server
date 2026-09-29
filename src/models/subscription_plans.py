from sqlalchemy import Integer, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from typing import Optional

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(String(255), unique=True)

    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))

    amount_usd: Mapped[float] = mapped_column(Float)
    duration_hours: Mapped[int] = mapped_column(Integer)

class SubscriptionPlanCreate(BaseModel):
    offer_id: str

    title: str
    description: str

    amount_usd: float
    duration_hours: int

class SubscriptionPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    amount_usd: Optional[float] = None
    duration_hours: Optional[int] = None

class SubscriptionPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    offer_id: str
    
    title: str
    description: str
    
    amount_usd: float
    duration_hours: int