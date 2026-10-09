import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings

from src.models.user import User

@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    user = User(
        telegram_id=settings.TEST_TELEGRAM_ID
    )

    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    return user