from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone

from ..db.model import Base

from .promocode import Promocode


class Promouse(Base):
    __tablename__ = "promouses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    code_id: Mapped[int] = mapped_column(Integer, ForeignKey("promocodes.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    promocode: Mapped["Promocode"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "code_id", name="uq_promouse_user_code"),
    )


class PromouseCreate(BaseModel):
    user_id: int
    code_id: int


class PromouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    code_id: int
    timestamp: datetime