from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional


class OrderItem(SQLModel, table=True):
    id: int | None= Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    quantity: int
    price: float

    order: Optional["Order"]= Relationship(back_populates="items")

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    status: str
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    items: list[OrderItem] = Relationship(back_populates="order")

OrderItem.order = Relationship(back_populates="items")
