from fastapi import FastAPI

from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    from ..db.database import engine
    from ..db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

from .config import settings
from ..api import api_v1_router

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(api_v1_router)