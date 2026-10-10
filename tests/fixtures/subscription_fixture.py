import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings

from src.models.user import User
from src.models.subscription_plans import SubscriptionPlan
from src.models.user_subscriptions import UserSubscription

@pytest_asyncio.fixture
async def fake_user_subscription(
    db_session: AsyncSession,
    user: User,
    subscription_plan: SubscriptionPlan
) -> UserSubscription:
    user_subscription = UserSubscription(
        invoice_id="ff153b9a-1c2a-4331-a035-dd9ee9ef55e",
        user_id=user.id,
        plan_id=subscription_plan.id,
        status="new"
    )

    db_session.add(user_subscription)
    await db_session.flush()
    await db_session.refresh(user_subscription)

    return user_subscription