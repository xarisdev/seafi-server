from typing import Optional
from pydantic import BaseModel, ConfigDict

from datetime import datetime

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    username: Optional[str]
    created_at: datetime

    language: Optional[str]

    is_premium: bool
    premium_expires_at: Optional[datetime]