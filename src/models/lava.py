from pydantic import BaseModel

class ProductSchema(BaseModel):
    id: str
    title: str
    description: str | None
    offer_id: str
    offer_name: str
    offer_description: str | None