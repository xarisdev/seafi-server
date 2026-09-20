from pydantic import BaseModel

class UserRegistrationRequest(BaseModel):
    username: str
    telegram_id: int

class FilterCreateRequest(BaseModel):
    telegram_id: int
    price_min: int = 0
    price_max: int = 0
    owner: str = "all"

class PaymentLinkSchema(BaseModel):
    id: str
    status: str
    amountTotal: dict
    paymentUrl: str
    payment_timeout_s: int