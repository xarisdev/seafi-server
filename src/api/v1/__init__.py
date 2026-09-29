from fastapi import APIRouter, Depends
# routers
from .filters import router as filter_fouter
from .internal import router as internal_router
from .payments import router as payment_router
from .products import router as product_router
from .plans import router as plan_router
from .users import router as user_router
from .websocket import router as ws_router

from ..dependencies import verify_x_api_key

verify_router = APIRouter(dependencies=[Depends(verify_x_api_key)])
verify_router.include_router(user_router)
verify_router.include_router(plan_router)
verify_router.include_router(filter_fouter)
verify_router.include_router(payment_router)
verify_router.include_router(internal_router)

default_router = APIRouter()
default_router.include_router(product_router)
default_router.include_router(ws_router)

router = APIRouter(prefix='/v1')
router.include_router(verify_router)
router.include_router(default_router)