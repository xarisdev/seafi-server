import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.api.dependencies import verify_x_api_key
from src.db.database import get_db
from src.db.model import Base
from src.core.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(init_test_db):
    engine = init_test_db

    async with engine.connect() as connection:
        transaction = await connection.begin()

        Session = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession
        )
        async with Session() as session:
            async def _override_get_db():
                yield session

            app.dependency_overrides[get_db] = _override_get_db
            
            yield session
            
            app.dependency_overrides.clear()
            await transaction.rollback()

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def _override_verify_x_api_key():
        return None

    async def _override_verify_x_admin_key():
        return None

    app.dependency_overrides[verify_x_api_key] = _override_verify_x_api_key
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as _client:
        yield _client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def auth_client(db_session):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test",) as _client:
        yield _client