from fastapi import APIRouter
# routers
from .users import router as user_router
from .filters import router as filter_fouter
...
# include
router = APIRouter(prefix='/v1')
router.include_router(user_router)
router.include_router(filter_fouter)
...