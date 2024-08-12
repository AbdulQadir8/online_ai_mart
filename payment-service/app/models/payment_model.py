from sqlmodel import SQLModel, Field
from datetime import datetime


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int
    user_id: int
    amount: float
    currency: str
    status: str = "pending"
    stripe_checkout_session_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payment.id")
    status: str = "initiated"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CheckoutSessionRequest(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    amount: float
    currency: str
    success_url: str
    cancel_url: str

class CheckoutSessionResponse(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    checkout_url: str