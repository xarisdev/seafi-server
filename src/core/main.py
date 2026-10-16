from contextlib import asynccontextmanager

from . import logger

from fastapi import FastAPI

from .middlewares import LoggingMiddleware
from ..api import router as api_router

from ..db.database import engine
from ..db.model import Base

from ..services.websocket import websocket_manager

from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await websocket_manager.disconnect()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(LoggingMiddleware)

app.include_router(api_router)