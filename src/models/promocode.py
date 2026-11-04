from typing import Optional

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone

from ..db.model import Base


class Promocode(Base):
    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)

    plan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class PromocodeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    plan_id: Optional[int] = None
    duration_hours: Optional[int] = None
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None


class PromocodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    plan_id: int | None
    duration_hours: int | None
    usage_limit: int | None
    expires_at: datetime | None
    created_at: datetime


class PromocodeUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: Optional[str] = None
    plan_id: Optional[int] = None
    duration_hours: Optional[int] = None
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None