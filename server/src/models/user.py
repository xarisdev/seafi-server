from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base

from pydantic import BaseModel, ConfigDict

from typing import Optional
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    language: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)

    is_premium: Mapped[bool] = mapped_column(default=False)
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    language: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    language: Optional[str] = None

    is_premium: Optional[bool] = None
    premium_expires_at: Optional[datetime] = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    username: Optional[str] = None
    created_at: datetime

    language: Optional[str] = None

    is_premium: bool
    premium_expires_at: Optional[datetime] = None