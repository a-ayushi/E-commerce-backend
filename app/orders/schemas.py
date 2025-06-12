from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class OrderDetailOut(OrderOut):
    items: List[OrderItemOut]
