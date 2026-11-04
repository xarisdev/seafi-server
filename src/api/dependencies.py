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

def _validate_secret(secret_value: str | None, expected_secret: str, header_name: str, secret_label: str) -> bool:
    if not secret_value:
        raise UnauthorizedException(f"Missing {secret_label} in header '{header_name}'")

    is_valid = hmac.compare_digest(secret_value, expected_secret)
    if not is_valid:
        raise ForbiddenException(f"Invalid {secret_label} in header '{header_name}'")

    return True


async def verify_x_api_key(x_api_key: Annotated[str, Header(alias="X-Api-Key")]):
    return _validate_secret(
        secret_value=x_api_key,
        expected_secret=settings.X_API_KEY,
        header_name="X-Api-Key",
        secret_label="API key",
    )


async def verify_lava_webhook_secret(lava_webhook_secret: Annotated[str, Header(alias="X-Api-Key")]):
    # Lava contract sends the webhook secret in the X-Api-Key header.
    return _validate_secret(
        secret_value=lava_webhook_secret,
        expected_secret=settings.LAVA_WEBHOOK_SECRET,
        header_name="X-Api-Key",
        secret_label="Lava webhook secret",
    )

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
        schema_to_select=FilterRead,
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