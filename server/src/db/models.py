from sqlalchemy import BigInteger, String, DateTime, Integer
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