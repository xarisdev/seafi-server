from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.model import Base


class ScraperState(Base):
    __tablename__ = "scraper_states"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    notifications_enabled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ScraperStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    notifications_enabled_at: datetime