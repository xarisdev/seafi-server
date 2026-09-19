import asyncio

from fastapi import FastAPI

from .workers_manager import workers_manager

from ..services.websocket import websocket_manager
from ..services.notifications_queue import notification_queue

from .config import settings
from ..api import router as api_router

from . import logger
from .middlewares import LoggingMiddleware

from ..db.database import engine
from ..db.model import Base

from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    notification_queue_worker = asyncio.create_task(notification_queue.start_worker())
    await workers_manager.start()

    yield

    notification_queue_worker.cancel()
    await workers_manager.stop()

    await websocket_manager.disconnect() # single M2M connect

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(LoggingMiddleware)

app.include_router(api_router)