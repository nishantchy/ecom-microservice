from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    order_number: int
    status: str = Field(default="pending")
    total_amount: str
    payment_method: str = Field(default="cash_on_delivery")
    shipping_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    quantity: int
    total_amt: int
    order: Optional[Order] = Relationship(back_populates="items")