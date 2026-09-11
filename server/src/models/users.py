from pydantic import BaseModel

class UserRegistrationRequest(BaseModel):
    secret_key: str
    username: str
    telegram_id: int