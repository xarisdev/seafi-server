from fastcrud import FastCRUD

from ..models.promouse import Promouse, PromouseCreate, PromouseRead

CRUDPromouses = FastCRUD[Promouse, PromouseCreate, dict, PromouseRead, dict, dict]
crud_promouses = CRUDPromouses(Promouse)