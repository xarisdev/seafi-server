from fastapi import APIRouter

from .v1 import router as v1_router

api_v1_router = APIRouter(prefix='/api')
api_v1_router.include_router(v1_router)