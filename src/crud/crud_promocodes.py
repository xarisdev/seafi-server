from fastcrud import FastCRUD

from ..models.promocode import Promocode, PromocodeCreate, PromocodeRead, PromocodeUpdate

CRUDPromocodes = FastCRUD[Promocode, PromocodeCreate, PromocodeUpdate, PromocodeRead, dict, PromocodeUpdate]
crud_promocodes = CRUDPromocodes(Promocode)