from typing import Optional
from pydantic import BaseModel, ConfigDict

from datetime import datetime

class ResponseSchema(BaseModel):
    url: str
    status_code: int | None = None
    data: dict | str | None = None
    error: None | str = None

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    username: Optional[str]
    created_at: datetime

    is_premium: bool
    premium_expires_at: Optional[datetime]