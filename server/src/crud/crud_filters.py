from fastcrud import FastCRUD

from ..models.filter import Filter, FilterCreate, FilterUpdate, FilterRead

CRUDUser = FastCRUD[Filter, FilterCreate, FilterUpdate, FilterRead, dict, FilterUpdate]
crud_filters = CRUDUser(Filter)