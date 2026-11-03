from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from ..db.model import Base
from ..enums.advertisement import EnumAdsSourceId, EnumAdsType, EnumAdsOwner

from pydantic import BaseModel, ConfigDict

from typing import Optional

class Advertisement(Base):
    __tablename__ = "advertisements"
    __table_args__ =  (
        UniqueConstraint("ads_id", "ads_source", name="uq_id_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    
    ads_id: Mapped[str] = mapped_column(String)
    ads_source: Mapped[EnumAdsSourceId] = mapped_column(Integer)

    url: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)

    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    city: Mapped[str] = mapped_column(String)
    
    type: Mapped[EnumAdsType] = mapped_column(String)
    owner: Mapped[Optional[EnumAdsOwner]] = mapped_column(String, default=EnumAdsOwner.ANY)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class AdvertisementCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ads_id: str
    ads_source: EnumAdsSourceId

    url: str
    title: str
    price: Optional[int] = None
    city: str
    type: EnumAdsType
    owner: Optional[EnumAdsOwner] = EnumAdsOwner.ANY

class AdvertisementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ads_id: str
    ads_source: EnumAdsSourceId
    url: str
    title: str
    price: int | None
    city: str
    type: EnumAdsType
    owner: EnumAdsOwner
    
    created_at: datetime
    last_seen_at: datetime

class AdvertisementUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = None
    price: Optional[int] = None

    last_seen_at: datetime