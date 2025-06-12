from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str
    image_url: Optional[HttpUrl] = None

class ProductUpdate(ProductCreate):
    pass

class ProductOut(ProductCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
