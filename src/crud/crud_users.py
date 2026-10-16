from fastcrud import FastCRUD

from ..models.user import User, UserCreate, UserRead

CRUDUser = FastCRUD[User, UserCreate, dict, UserRead, dict, dict]
crud_users = CRUDUser(User)