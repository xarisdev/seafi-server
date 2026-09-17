from pydantic import BaseModel

class Response(BaseModel):
    url: str
    status_code: int | None = None
    data: dict | str | None = None
    error: None | str = None