from sqlalchemy import String, Integer, DateTime, UniqueConstraint, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from ..db.model import Base
from ..enums.ads_delivery import EnumAdsDeliveryStatus

from pydantic import BaseModel, ConfigDict

from typing import Optional

class AdvertisementDelivery(Base):
    __tablename__ = "advertisement_deliveries"
    __table_args__ = (
        UniqueConstraint("ads_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    ads_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("advertisements.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))

    status: Mapped[EnumAdsDeliveryStatus] = mapped_column(String, default=EnumAdsDeliveryStatus.PENDING)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

class AdvertisementDeliveryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ads_id: int
    user_id: int

    status: Optional[EnumAdsDeliveryStatus] = EnumAdsDeliveryStatus.PENDING
    attempts: Optional[int] = 0

class AdvertisementDeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ads_id: int
    user_id: int

    status: EnumAdsDeliveryStatus
    attempts: int

    created_at: datetime
    sent_at: datetime | None

class AdvertisementDeliveryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempts: int
    status: Optional[EnumAdsDeliveryStatus] = None
    sent_at: Optional[datetime] = None