from pydantic import BaseModel

class Notification(BaseModel):
    telegram_id: int
    data: dict