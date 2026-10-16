import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings

from src.models.plan import Plan

@pytest_asyncio.fixture
async def subscription_plan(db_session: AsyncSession) -> Plan:
    subscription_plan = Plan(
        offer_id="TEST-OFFER-ID",
        title="TEST-TITLE",
        description="TEST-DESCRIPTION",
        amount=10.0,
        duration=24
    )

    db_session.add(subscription_plan)
    await db_session.flush()
    await db_session.refresh(subscription_plan)

    return subscription_plan