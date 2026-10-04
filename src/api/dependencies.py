import hmac

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Header, Depends, Query
from ..core.exceptions.http_exceptions import NotFoundException, UnauthorizedException, ForbiddenException

from ..core.config import settings
from ..db.database import get_db

from ..crud.crud_users import crud_users
from ..models.user import UserRead

# ------------ Verify ------------

async def verify_x_api_key(x_api_key: Annotated[str, Header(alias="X-Api-Key")]):
    if not x_api_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(x_api_key, settings.APP_TOKEN)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

async def verify_lava_webhook_key(lava_webhook_key: Annotated[str, Query(alias="X-Api-Key")]):
    if not lava_webhook_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(lava_webhook_key, settings.LAVA_API_PASSWORD)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

    return is_valid

# --------- User ------------

async def _find_user(db: AsyncSession, telegram_id: int):
    user = await crud_users.get(
        db=db,
        schema_to_select=UserRead,
        return_as_model=True,
        one_or_none=True,
        telegram_id=telegram_id
    )
    if not user:
        raise NotFoundException
    
    return user

async def get_user_by_path(
    telegram_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRead:
    return await _find_user(db=db, telegram_id=telegram_id)

async def get_user_by_query(
    telegram_id: Annotated[int, Query()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRead:
    return await _find_user(db=db, telegram_id=telegram_id)