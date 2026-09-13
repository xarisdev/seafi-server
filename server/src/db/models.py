from sqlalchemy import BigInteger, String, DateTime, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from typing import Optional
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    subscription_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    filter_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    # Lalafo filters
    price_min: Mapped[int] = mapped_column(Integer, default=0)
    price_max: Mapped[int] = mapped_column(Integer, default=0)
    author_type: Mapped[str] = mapped_column(String(50), default="all")