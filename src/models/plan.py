from typing import Optional

from sqlalchemy import Integer, String, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from decimal import Decimal
from datetime import datetime, timezone

from ..db.model import Base

MAX_DIGITS = 4
DECIMAL_PLACES = 2
AMOUNT_FIELD = Field(
    max_digits=MAX_DIGITS,
    decimal_places=DECIMAL_PLACES,
    ge=0
)

class Plan(Base):
    __tablename__ = "plans"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(String, unique=True)

    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(512))

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=MAX_DIGITS, scale=DECIMAL_PLACES)
    )
    duration: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class PlanCreate(BaseModel):
    offer_id: str

    title: str
    description: str

    amount: Decimal = AMOUNT_FIELD
    duration: int

class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    amount: Optional[Decimal] = Field(
        default=None,
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        ge=0
    )
    duration: Optional[int] = None

class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    offer_id: str
    title: str
    description: str
    amount: Decimal = AMOUNT_FIELD
    duration: int
    created_at: datetime

    @field_serializer('amount')
    def serialize_amount(self, amount: Decimal) -> str:
        return f"{amount:.2f}"