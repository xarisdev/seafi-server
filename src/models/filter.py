from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from typing import Optional

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    property_type: Mapped[str] = mapped_column(String(255), default="apartment")
    deal_type: Mapped[str] = mapped_column(String(255), default="rent")

    owner_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    price_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class FilterCreate(BaseModel):
    user_id: int

class FilterUpdate(BaseModel):
    city: str
    property_type: Optional[str] = None
    deal_type: Optional[str] = None

    owner_type: Optional[str] = None

    price_min: Optional[int] = None
    price_max: Optional[int] = None

class FilterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    city: str | None
    property_type: str
    deal_type: str

    owner_type: str | None = None

    price_min: int | None = None
    price_max: int | None = None