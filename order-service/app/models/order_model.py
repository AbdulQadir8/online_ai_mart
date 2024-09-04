from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List



# class Order(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: int
#     status: str
#     total_amount: float
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     items: List["OrderItem"] = Relationship(back_populates="order")


# class OrderItem(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     product_id: int
#     quantity: int
#     price: float
#     order_id: int | None = Field(default=None,foreign_key="order.id")
#     order: Order | None = Relationship(back_populates="items")



#This class will contain the shared properties between different Order schemas.
class OrderBase(SQLModel):
    user_id: int
    status: str
    total_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

#This schema extends OrderBase and adds the items field for creating a new order.
class CreateOrderItem(SQLModel):
    product_id: int
    quantity: int
    price: float

class CreateOrder(OrderBase):
    items: List[CreateOrderItem] = Field(default_factory=list)


#This schema extends OrderBase and makes all fields optional to allow partial updates.
class UpdateOrder(OrderBase):
    user_id: int | None = None
    status: str | None = None
    total_amount: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)



#This class will contain the shared properties for the OrderItem schema.
class OrderItemBase(SQLModel):
    product_id: int
    quantity: int
    price: float
    order_id: int | None = Field(default=None, foreign_key="order.id")


#This schema will extend OrderItemBase for creating a new order item.
class CreateOrderItem(OrderItemBase):
    pass

#This schema will extend OrderItemBase and make all fields optional to allow partial updates.
class UpdateItem(OrderItemBase):
    product_id: int | None = None
    quantity: int | None = None
    price: float | None = None
    order_id: int | None = None 

#These are your original database models, unchanged, as they already align with the pattern used for User.
class Order(OrderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(OrderItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order: Order | None = Relationship(back_populates="items")




