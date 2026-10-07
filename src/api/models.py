from pydantic import BaseModel, ConfigDict

from ..models.user_subscriptions import UserSubscriptionRead
from ..integrations.lava.models import InvoiceSchema

class CreateLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invoice: InvoiceSchema
    subscription: UserSubscriptionRead

class UserSubscriptionsResponse(BaseModel):
    data: list[UserSubscriptionRead]
    total_count: int

class FilterCreateRequest(BaseModel):
    telegram_id: int
    price_min: int = 0
    price_max: int = 0
    owner: str = "all"