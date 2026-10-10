from typing import Optional

from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from ..db.model import Base

MAX_DIGITS = 4
DECIMAL_PLACES = 2
AMOUNT_FIELD = Field(max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, ge=0)

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(String(255), unique=True)

    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))

    amount_usd: Mapped[Decimal] = mapped_column(Numeric(precision=MAX_DIGITS, scale=DECIMAL_PLACES))
    duration_hours: Mapped[int] = mapped_column(Integer)

class SubscriptionPlanCreate(BaseModel):
    offer_id: str

    title: str
    description: str

    amount_usd: Decimal = AMOUNT_FIELD
    duration_hours: int

class SubscriptionPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    amount_usd: Optional[Decimal] = Field(default=None, max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES, ge=0)
    duration_hours: Optional[int] = None

class SubscriptionPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    offer_id: str
    
    title: str
    description: str
    
    amount_usd: Decimal = AMOUNT_FIELD
    duration_hours: int

    @field_serializer('amount_usd')
    def serialize_amount(self, amount: Decimal) -> str:
        return f"{amount:.2f}"