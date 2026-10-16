import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings

from src.models.user import User
from src.models.plan import Plan
from src.models.subscription import Subscription

@pytest_asyncio.fixture
async def fake_user_subscription(
    db_session: AsyncSession,
    user: User,
    subscription_plan: Plan
) -> Subscription:
    user_subscription = Subscription(
        user_id=user.id,
        plan_id=subscription_plan.id,
        invoice_id="ff153b9a-1c2a-4331-a035-dd9ee9ef55e",
        source="fake"
    )

    db_session.add(user_subscription)
    await db_session.flush()
    await db_session.refresh(user_subscription)

    return user_subscription