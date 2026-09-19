from pydantic import BaseModel

class ResponseSchema(BaseModel):
    url: str
    status_code: int | None = None
    data: dict | str | None = None
    error: None | str = None

class UserSchema(BaseModel):
    id: int
    telegram_id: int
    username: str
    created_at: str
    subscription_id: int | None