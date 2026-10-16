from fastcrud import FastCRUD

from ..models.invoice import Invoice, InvoiceCreate, InvoiceRead, InvoiceUpdate

CRUDInvoices = FastCRUD[Invoice, InvoiceCreate, InvoiceUpdate, InvoiceRead, dict, InvoiceUpdate]
crud_invoices = CRUDInvoices(Invoice)