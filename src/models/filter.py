from sqlalchemy import BigInteger, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from typing import Optional
from datetime import datetime, timezone

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    price_min: Mapped[int] = mapped_column(Integer, default=-1)
    price_max: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class FilterCreate(BaseModel):
    telegram_id: int

class FilterUpdate(BaseModel):
    telegram_id: int

    city: Optional[str]
    price_min: int 
    price_max: int

class FilterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int

    city: str
    price_min: int 
    price_max: int