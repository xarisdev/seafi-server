from pydantic import BaseModel

class WebhookEventPayment(BaseModel):
    eventType: str
    product: dict
    #{
    #    id: d31384b8-e412-4be5-a2ec-297ae6666c8f,
    #    title: Тестовый продукт
    #},
    buyer: dict # {email: test@lava.top}
    contractId: str
    amount: float
    currency: str
    timestamp: str
    status: str
    errorMessage: str

class WebhookEventRefund(BaseModel):
    event_id: str
    event_type: str
    created_at: str
    data: dict | None
    snake_case: dict | None

class WebhookRequest(BaseModel):
    eventType: str

    product: dict[str, str]
    buyer: dict[str, str]

    contractId: str
    amount: float
    currency: str

    timestamp: str
    status: str
    errorMessage: str | None