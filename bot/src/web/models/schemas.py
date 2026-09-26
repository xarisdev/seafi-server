from typing import Any
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    url: str
    status_code: int | None = None
    data: Any | None = None
    error: None | str = None