import asyncio
import logging

from sqlalchemy import func, select

from ..core.config import settings
from ..db.database import AsyncSessionLocal, engine
from .advertisement_delivery import (
    claim_pending_deliveries,
    expire_ineligible_deliveries,
    load_delivery_messages,
    recover_expired_deliveries,
)
from .lalafo_scraper import notify_admin, scrape_all_sources
from .lalafo_storage import create_matching_deliveries, ensure_notification_baseline
from .websocket import websocket_manager

logger = logging.getLogger("services.lalafo_scheduler")

ADVISORY_LOCK_KEY = 73190420261104
MATCH_INTERVAL_SECONDS = 5 * 60


async def _scraper_loop() -> None:
    while True:
        await scrape_all_sources()


async def _delivery_loop() -> None:
    while True:
        await asyncio.sleep(MATCH_INTERVAL_SECONDS)
        try:
            async with AsyncSessionLocal() as db:
                created = await create_matching_deliveries(db)
                await recover_expired_deliveries(db)
                await expire_ineligible_deliveries(db)

                if websocket_manager.is_connected:
                    delivery_ids = await claim_pending_deliveries(db)
                    await db.commit()
                    messages = await load_delivery_messages(db, delivery_ids)
                    for message in messages:
                        await websocket_manager.put_payload(message)
                else:
                    await db.commit()

            if created:
                logger.info("Created %s matching advertisement deliveries", created)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Advertisement matching/delivery cycle failed")
            await notify_admin("advertisement-delivery", "Matching or delivery cycle failed")


async def run_background_jobs() -> None:
    if settings.APP_ENV.lower() == "test":
        return

    try:
        async with engine.connect() as lock_connection:
            acquired = await lock_connection.scalar(
                select(func.pg_try_advisory_lock(ADVISORY_LOCK_KEY))
            )
            await lock_connection.commit()
            if not acquired:
                logger.info("Another API process owns the background job lock")
                return

            try:
                async with AsyncSessionLocal() as db:
                    baseline = await ensure_notification_baseline(db)
                    await db.commit()
                logger.info("Lalafo notification baseline is %s", baseline.isoformat())

                tasks = [
                    asyncio.create_task(_scraper_loop(), name="lalafo-scraper"),
                    asyncio.create_task(_delivery_loop(), name="advertisement-delivery"),
                ]
                try:
                    await asyncio.gather(*tasks)
                finally:
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                await lock_connection.scalar(
                    select(func.pg_advisory_unlock(ADVISORY_LOCK_KEY))
                )
                await lock_connection.commit()
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Lalafo background jobs stopped unexpectedly")