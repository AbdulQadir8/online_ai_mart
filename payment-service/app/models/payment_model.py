from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import condecimal
from typing import List


# class Payment(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     order_id: int
#     user_id: int
#     amount: float
#     currency: str
#     status: str = "pending"
#     stripe_checkout_session_id: str | None = None
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)

# class Transaction(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     payment_id: int = Field(foreign_key="payment.id")
#     status: str = "initiated"
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)


from pydantic import condecimal


# Base model for common fields in payment-related models
class PaymentBase(SQLModel):
    order_id: int
    user_id: int
    amount: int  # Amount must be positive with 2 decimal places
    currency: str  # You could add validation to limit to specific currencies
    status: str = "pending"  # Status default to "pending"
    stripe_checkout_session_id: str | None = None  # Optional Stripe session ID


# Payment model for database table
class Payment(PaymentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # One-to-many relationship with Transaction
    transactions: List["Transaction"] = Relationship(back_populates="payment",cascade_delete=True)



# Model for creating a new Payment (no id, auto-generated timestamps)
class CreatePayment(PaymentBase):
    pass


# Model for updating Payment (all fields optional)
class UpdatePayment(SQLModel):
    order_id: int | None = None
    user_id: int | None = None
    amount: condecimal(gt=0, decimal_places=2) | None = None
    currency: str | None = None
    status: str | None = None
    stripe_checkout_session_id: str | None = None
    updated_at: str | None = Field(default_factory=datetime.utcnow)


# Model for returning public-facing Payment data (read-only)
class PublicPayment(PaymentBase):
    id: int
    created_at: datetime
    updated_at: datetime


# Base model for common fields in transaction-related models
class TransactionBase(SQLModel):
    status: str = "initiated"  # Default status to "initiated"


# Transaction model for the database table
class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # Foreign key with relationship to Payment
    payment_id: int = Field(foreign_key="payment.id",ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationship back to Payment
    payment: Payment = Relationship(back_populates="transactions")


# Model for creating a new Transaction (excluding `id`, auto-generated timestamps)
class CreateTransaction(TransactionBase):
    payment_id: int  # Payment ID is required when creating a transaction


# Model for updating Transaction (all fields optional)
class UpdateTransaction(SQLModel):
    status: str | None = None
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)


# Model for returning public-facing Transaction data (read-only)
class PublicTransaction(TransactionBase):
    id: int
    payment_id: int
    created_at: datetime
    updated_at: datetime



class CheckoutSessionRequest(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    amount: float
    currency: str
    success_url: str
    cancel_url: str

class CheckoutSessionResponse(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    checkout_url: str