from pydantic import BaseModel

class CreateUser(BaseModel):
    telegram_id: int
    username: str