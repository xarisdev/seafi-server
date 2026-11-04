from contextlib import asynccontextmanager
import asyncio

from . import logger

from fastapi import FastAPI

from .middlewares import LoggingMiddleware
from ..api import router as api_router

from ..db.database import engine
from ..db.model import Base

from ..models.advertisement import Advertisement
from ..models.advertisement_delivery import AdvertisementDelivery
from ..models.scraper_state import ScraperState

from ..services.websocket import websocket_manager
from ..services.lalafo_scheduler import run_background_jobs

from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    jobs_task = asyncio.create_task(run_background_jobs(), name="seafi-background-jobs")
    try:
        yield
    finally:
        jobs_task.cancel()
        await asyncio.gather(jobs_task, return_exceptions=True)

        await websocket_manager.disconnect()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.add_middleware(LoggingMiddleware)

app.include_router(api_router)