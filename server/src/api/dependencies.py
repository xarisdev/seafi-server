import hmac

from typing import Annotated

from fastapi import HTTPException, Header, status

from ..core.config import settings

async def verify_secret_key(x_api_key: Annotated[str, Header(alias="X-Api-Key")]):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    is_valid = hmac.compare_digest(x_api_key, settings.APP_TOKEN)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )