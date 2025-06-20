from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    total_amt: int

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderItemRead(OrderItemBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: str
    order_number: int
    status: str
    total_amount: str
    payment_method: str = "cash_on_delivery"
    shipping_address: Optional[str] = None

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderRead(OrderBase):
    id: int
    created_at: datetime
    items: List[OrderItemRead] = []

    class Config:
        orm_mode = True
