from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from pydantic import validator

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    quantity: int
    price: float

    order: Optional["Order"] = Relationship(back_populates="items")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    status: str
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    items: List[OrderItem] = Relationship(back_populates="order")

    @validator("created_at", "updated_at", pre=True, always=True)
    def validate_datetime(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

OrderItem.order = Relationship(back_populates="items")
