from pydantic import BaseModel

class UserRegistrationRequest(BaseModel):
    username: str
    telegram_id: int