from sqlalchemy import Integer, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone

from ..db.model import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

class UserCreate(BaseModel):
    telegram_id: int

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int

    created_at: datetime