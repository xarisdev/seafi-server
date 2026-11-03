from sqlalchemy import BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base
from ..enums.advertisement import EnumAdsType, EnumAdsOwner

from pydantic import BaseModel, ConfigDict

from typing import Optional

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)

    city: Mapped[str] = mapped_column(String, default="bishkek")
    
    ads_type: Mapped[Optional[EnumAdsType]] = mapped_column(String, default=EnumAdsType.RENT)
    ads_owner: Mapped[Optional[EnumAdsOwner]] = mapped_column(String, default=EnumAdsOwner.ANY)

    min_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

class FilterCreate(BaseModel):
    user_id: int

class FilterUpdate(BaseModel):
    city: Optional[str] = None
    
    ads_type: Optional[EnumAdsType] = None
    ads_owner: Optional[EnumAdsOwner] = None

    min_price: Optional[int] = None
    max_price: Optional[int] = None

class FilterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    city: str
    ads_type: EnumAdsType
    ads_owner: EnumAdsOwner | None
    min_price: int | None
    max_price: int | None