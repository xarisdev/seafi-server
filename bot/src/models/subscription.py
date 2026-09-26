from pydantic import BaseModel

class SubscriptionRead(BaseModel):
    id: int
    offer_id: str
    title: str
    description: str
    amount: float
    duration_hours: int

class SubscriptionCreate(BaseModel):
    offer_id: str
    title: str
    description: str
    amount: float
    duration_hours: int