from sqlmodel import SQLModel, Field
from datetime import date


class ProductBase(SQLModel):
    name: str  # Name is required
    description: str  
    price: int # Price should be a positive number with 2 decimal places
    expiry: date | None = None  # Expiry date can be None
    brand: str | None = None  # Optional field with length validation
    weight: str | None = None  # Assuming weight is a string (e.g., "1kg", "500g")
    category: str | None  # Predefined by platform, should have constraints
    sku: str | None = None  # SKU should be a valid string


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)  # Auto-generated primary key


# Model used for creating a new product. Doesn't require 'id' since it's auto-generated.
class CreateProduct(ProductBase):
    pass


# Model used for public representation of the product (read-only).
class PublicProduct(ProductBase):
    id: int  # 'id' is included since it's needed when exposing the product publicly


# Model used for updating a product. All fields are optional for partial updates.
class UpdateProduct(SQLModel):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    expiry: date | None = None
    brand: str | None = None
    weight: str | None = None
    category: str | None = None
    sku: str | None = None
