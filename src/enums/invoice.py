from enum import Enum
from decimal import Decimal

class EnumInvoiceStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class EnumInvoiceCurrency(str, Enum):
    USD = "USD"
    RUB = "RUB"

class EnumInvoiceCurrencyExchange(Decimal, Enum):
    USD = Decimal("1.00")
    RUB = Decimal("85.00")