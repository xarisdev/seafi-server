from fastapi import APIRouter
# routers
from .filters import router as filter_fouter
from .internal import router as internal_router
from .payments import router as payment_router
from .users import router as user_router
from .websocket import router as ws_router
...
# include
router = APIRouter(prefix='/v1')
router.include_router(filter_fouter)
router.include_router(internal_router)
router.include_router(payment_router)
router.include_router(user_router)
router.include_router(ws_router)
...