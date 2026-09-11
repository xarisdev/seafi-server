from fastapi import APIRouter
# routers
from .users import router as user_router
...
# include
router = APIRouter(prefix='/v1')
router.include_router(user_router)
...