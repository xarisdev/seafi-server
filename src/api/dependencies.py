import hmac

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Header, Depends, Query
from ..core.exceptions.http_exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException
)
from ..db.database import get_db
from ..crud.crud_users import crud_users
from ..crud.crud_filters import crud_filters
from ..models.user import UserRead
from ..models.filter import FilterRead

from ..core.config import settings

# ------------ Verify ------------

async def verify_x_api_key(x_api_key: Annotated[str, Header(alias="X-Api-Key")]):
    if not x_api_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(x_api_key, settings.APP_TOKEN)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

async def verify_lava_webhook_key(lava_webhook_key: Annotated[str, Header(alias="X-Api-Key")]):
    if not lava_webhook_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(lava_webhook_key, settings.LAVA_API_PASSWORD)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

    return is_valid

# ------------ User ------------

async def _find_user(db: AsyncSession, **kwargs):
    user = await crud_users.get(
        db=db,
        schema_to_select=UserRead,
        return_as_model=True,
        one_or_none=True,
        **kwargs
    )

    if user is None:
        raise NotFoundException(f"User with params: {kwargs} not found")
    
    return user

async def user_by_path(
    telegram_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRead:
    return await _find_user(db=db, telegram_id=telegram_id)

async def user_by_query(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[int | None, Query(alias="id")] = None,
    telegram_id: Annotated[int | None, Query(alias="telegram_id")] = None
) -> UserRead:
    
    if id is not None:
        return await _find_user(db=db, id=id)

    elif telegram_id is not None:
        return await _find_user(db=db, telegram_id=telegram_id)

    else:
        raise BadRequestException("Required: 'user_id' or 'telegram_id'")

# ------------ Filter ------------

async def _find_filter(db: AsyncSession, **kwargs):
    db_filter = await crud_filters.get(
        db=db,
        schema_to_select=UserRead,
        return_as_model=True,
        one_or_none=True,
        **kwargs
    )

    if db_filter is None:
        raise NotFoundException(f"Filter with params: {kwargs} not found")
    
    return db_filter

async def get_filter_by_path(
    db: Annotated[AsyncSession, Depends(get_db)],
    id: int
) -> FilterRead:
    return await _find_filter(db=db, id=id)