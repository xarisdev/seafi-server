from pydantic import BaseModel

class ProductSchema(BaseModel):
    id: str
    title: str
    offer_id: str
    offer_name: str