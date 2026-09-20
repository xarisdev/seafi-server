import hmac

from typing import Annotated

from fastapi import Header
from ..core.exceptions.http_exceptions import UnauthorizedException, ForbiddenException

from ..core.config import settings

async def verify_secret_key(x_api_key: Annotated[str, Header(alias="X-Api-Key")]):
    if not x_api_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(x_api_key, settings.APP_TOKEN)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

async def verify_admin_key(x_admin_key: Annotated[str, Header(alias="X-Admin-Key")]):
    if not x_admin_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(x_admin_key, settings.ADMIN_ID)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

    return is_valid

async def verify_lava_webhook_key(lava_webhook_key: Annotated[str, Header(alias="Authorization")]):
    if not lava_webhook_key:
        raise UnauthorizedException("Missing API key")

    is_valid = hmac.compare_digest(lava_webhook_key, settings.LAVA_API_PASSWORD)
    if not is_valid:
        raise ForbiddenException("Invalid API key")

    return is_valid