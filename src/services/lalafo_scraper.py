import asyncio
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import AsyncSessionLocal
from ..integrations.lalafo.parser import LALAFO_SOURCES, LalafoSource, parse_lalafo_page
from .lalafo_storage import upsert_lalafo_listings

logger = logging.getLogger("services.lalafo_scraper")

REQUEST_TIMEOUT = httpx.Timeout(connect=10.0, read=25.0, write=10.0, pool=10.0)
MAX_PAGES_PER_SOURCE = 3
REQUEST_DELAY_SECONDS = 1.0
PARSER_INTERVAL_SECONDS = 90
USER_AGENT = "SeafiServer/1.0 (+https://seafi.xaris.space)"


async def scrape_source(
    source: LalafoSource,
    *,
    session_factory=AsyncSessionLocal,
    max_pages: int = MAX_PAGES_PER_SOURCE,
) -> int:
    page_url = source.url
    new_count = 0

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
    ) as client:
        for page_number in range(1, max_pages + 1):
            if page_number > 1:
                await asyncio.sleep(REQUEST_DELAY_SECONDS)

            response = await client.get(page_url)
            response.raise_for_status()
            parsed = parse_lalafo_page(
                response.text,
                source_owner=source.owner,
                page_url=str(response.url),
            )

            if not parsed.listings:
                logger.warning(
                    "Lalafo returned no listing cards for %s page %s",
                    source.key,
                    page_number,
                )
                break

            async with session_factory() as db:  # type: AsyncSession
                new_count += await upsert_lalafo_listings(db, parsed.listings)
                await db.commit()

            logger.info(
                "Lalafo source %s page %s: parsed %s listings, new %s",
                source.key,
                page_number,
                len(parsed.listings),
                new_count,
            )
            if parsed.next_page_url is None:
                break
            page_url = parsed.next_page_url

    return new_count


async def scrape_all_sources() -> None:
    for source in LALAFO_SOURCES:
        try:
            await scrape_source(source)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Lalafo parser %s failed; continuing with next source", source.key)
            await notify_admin(source.key, "Lalafo source parsing failed")

        await asyncio.sleep(PARSER_INTERVAL_SECONDS)


async def notify_admin(source: str, message: str) -> None:
    from datetime import UTC, datetime

    from ..core.config import settings
    from ..models.websocket import AdminAlertMessage
    from .websocket import websocket_manager

    admin_telegram_id = settings.ADMIN_TELEGRAM_ID
    if admin_telegram_id is None:
        logger.warning("ADMIN_TELEGRAM_ID is not configured; cannot send %s alert", source)
        return

    await websocket_manager.put_payload(
        AdminAlertMessage(
            telegram_id=admin_telegram_id,
            source=source,
            message=message,
            created_at=datetime.now(UTC),
        )
    )