from fastapi import APIRouter
# routers
from .users import router as user_router
from .filters import router as filter_fouter
from .payments import router as payment_router
from .websocket import router as ws_router
...
# include
router = APIRouter(prefix='/v1')
router.include_router(user_router)
router.include_router(filter_fouter)
router.include_router(payment_router)
router.include_router(ws_router)
...