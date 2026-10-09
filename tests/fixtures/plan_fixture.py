import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings

from src.models.subscription_plans import SubscriptionPlan

@pytest_asyncio.fixture
async def subscription_plan(db_session: AsyncSession) -> SubscriptionPlan:
    subscription_plan = SubscriptionPlan(
        offer_id="TEST-OFFER-ID",
        title="TEST-TITLE",
        description="TEST-DESCRIPTION",
        amount_usd=10.0,
        duration_hours=24
    )

    db_session.add(subscription_plan)
    await db_session.flush()
    await db_session.refresh(subscription_plan)

    return subscription_plan