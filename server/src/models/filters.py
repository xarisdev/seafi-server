from pydantic import BaseModel

class FilterCreateRequest(BaseModel):
    telegram_id: int
    price_min: int = 0
    price_max: int = 0
    owner: str = "all"