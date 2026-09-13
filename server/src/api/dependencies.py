from typing import Annotated

from fastapi import HTTPException, Header, status

from ..app.config import settings

async def verify_secret_key(secret_key: Annotated[str, Header(alias="authorization")]):
    if secret_key != settings.APP_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="wk")