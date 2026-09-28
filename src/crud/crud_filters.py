from fastcrud import FastCRUD

from ..models.filter import Filter, FilterCreate, FilterUpdate, FilterRead

CRUDFilter = FastCRUD[Filter, FilterCreate, FilterUpdate, FilterRead, dict, FilterUpdate]
crud_filters = CRUDFilter(Filter)