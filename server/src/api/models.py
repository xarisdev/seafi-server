from pydantic import BaseModel

class UserRegistrationRequest(BaseModel):
    username: str
    telegram_id: int

class FilterCreateRequest(BaseModel):
    telegram_id: int
    price_min: int = 0
    price_max: int = 0
    owner: str = "all"

class CreatePaymentLinkSchema(BaseModel):
    telegram_id: int
    comment: str