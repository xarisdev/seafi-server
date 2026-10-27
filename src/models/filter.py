from sqlalchemy import BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from enum import Enum
from pydantic import BaseModel, ConfigDict

from typing import Optional

class EnumFilterAdsType(str, Enum):
    RENT = "rent"
    SELL = "sell"

class EnumFilterAdsOwner(str, Enum):
    AGENT = "agent"
    OWNER = "owner"

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)

    city: Mapped[str] = mapped_column(String, default="bishkek")
    
    ads_type: Mapped[Optional[EnumFilterAdsType]] = mapped_column(String, default=EnumFilterAdsType.RENT)
    ads_owner: Mapped[Optional[EnumFilterAdsOwner]] = mapped_column(String, nullable=True)

    min_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

class FilterCreate(BaseModel):
    user_id: int

class FilterUpdate(BaseModel):
    city: Optional[str] = None
    
    ads_type: Optional[EnumFilterAdsType] = None
    ads_owner: Optional[EnumFilterAdsOwner] = None

    min_price: Optional[int] = None
    max_price: Optional[int] = None

class FilterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    city: str
    ads_type: EnumFilterAdsType
    ads_owner: EnumFilterAdsOwner | None
    min_price: int | None
    max_price: int | None