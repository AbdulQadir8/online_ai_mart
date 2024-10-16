from sqlmodel import SQLModel, Field
from typing import Literal
from enum import Enum

# Define an Enum for inventory status
class InventoryStatus(str, Enum):
    in_stock = "in_stock"
    out_of_stock = "out_of_stock"
    pre_order = "pre_order"
    discontinued = "discontinued"


# Base model with shared fields between InventoryItem and derived models
class InventoryItemBase(SQLModel):
    product_id: int  # ForeignKey to the Product model
    variant_id: int | None = None  # Optional variant of the product
    quantity: int # Quantity should be a non-negative integer
    status: InventoryStatus  # Predefined statuses


# Table model that stores inventory items
class InventoryItem(InventoryItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)  # Primary key, auto-generated


# Model used for creating new inventory items (excludes `id` since it's auto-generated)
class CreateInventoryItem(InventoryItemBase):
    pass


# Model for public-facing inventory data (read-only)
class PublicInventoryItem(InventoryItemBase):
    id: int  # Include the ID for identification


# Model used for updating an inventory item (all fields optional for partial updates)
class InventoryItemUpdate(SQLModel):
    product_id: int | None = None
    variant_id: int | None = None
    quantity: int | None = None  # Quantity must be a non-negative integer
    status: InventoryStatus | None = None


