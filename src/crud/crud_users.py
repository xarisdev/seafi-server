from fastcrud import FastCRUD

from ..models.user import User, UserCreate, UserUpdate, UserRead

CRUDUser = FastCRUD[User, UserCreate, UserUpdate, UserRead, dict, UserUpdate]
crud_users = CRUDUser(User)