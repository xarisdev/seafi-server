from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .invoice import EnumInvoiceStatus

class WebSocketMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    buyer_email: str
    contract_id: str
    invoice_status: EnumInvoiceStatus