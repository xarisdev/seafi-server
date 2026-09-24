from typing import Optional
from pydantic import BaseModel, ConfigDict

from datetime import datetime

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    username: str
    created_at: Optional[datetime] = None

    language: str

    is_premium: Optional[bool] = None
    premium_expires_at: Optional[datetime] = None

class UserInternal(BaseModel):
    telegram_id: int
    username: str
    language: Optional[str] = None