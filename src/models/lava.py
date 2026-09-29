from pydantic import BaseModel

class InvoiceSchema(BaseModel):
    id: str
    status: str
    amountTotal: dict
    paymentUrl: str
    # Custom
    payment_timeout_s: int

class ProductSchema(BaseModel):
    id: str
    title: str
    description: str | None
    offer_id: str
    offer_name: str
    offer_description: str | None