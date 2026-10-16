from enum import Enum
from decimal import Decimal

from typing import Annotated

from sqlalchemy import Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime, timezone

from ..db.model import Base

MAX_DIGITS = 10
DECIMAL_PLACES = 2

AmountField = Annotated[
    Decimal,
    Field(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        ge=0
    )
]

class EnumInvoiceStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class EnumInvoiceCurrency(str, Enum):
    USD = "USD"
    RUB = "RUB"

class EnumInvoiceCurrencyExchange(Decimal, Enum):
    USD = Decimal("1.00")
    RUB = Decimal("85.00")

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    contract_id: Mapped[str] = mapped_column(String, unique=True)
    payment_url: Mapped[str] = mapped_column(String)

    currency: Mapped[EnumInvoiceCurrency] = mapped_column(String)
    amount_total: Mapped[Decimal] = mapped_column(Numeric(MAX_DIGITS, DECIMAL_PLACES))

    status: Mapped[EnumInvoiceStatus] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class InvoiceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan_id: int
    user_id: int

    contract_id: str
    payment_url: str

    currency: EnumInvoiceCurrency
    amount_total: AmountField

    status: EnumInvoiceStatus

class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int
    user_id: int
    contract_id: str
    payment_url: str
    status: EnumInvoiceStatus
    currency: EnumInvoiceCurrency
    amount_total: AmountField
    created_at: datetime

    @field_serializer('amount_total')
    def serialize_amount_total(self, amount_total: Decimal) -> str:
        return f"{amount_total:.2f}"

class InvoiceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    status: EnumInvoiceStatus