import asyncio

from fastapi import FastAPI

from ..services.websocket import websocket_manager
from ..services.notifications_queue import notification_queue

from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    from ..db.database import engine
    from ..db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    notification_queue_worker = asyncio.create_task(notification_queue.start_worker())

    yield

    notification_queue_worker.cancel()
    await websocket_manager.disconnect()

from .config import settings
from ..api import router as api_router

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(api_router)