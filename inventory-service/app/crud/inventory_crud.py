from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.inventory_model import InventoryItem, InventoryItemUpdate
import logging
logging.basicConfig(level=logging.INFO)


# Add a New Inventory Item to the Database
def add_new_inventory_item(inventory_item_data: InventoryItem, session: Session):
    print("Adding Inventory Item to Database")

    session.add(inventory_item_data)
    session.commit()
    session.refresh(inventory_item_data)
    return inventory_item_data

# Get All Inventory Items from the Database
def get_all_inventory_items(session: Session):
    all_inventory_items = session.exec(select(InventoryItem)).all()
    return all_inventory_items


# Get an Inventory Item by ID
def get_inventory_item_by_id(inventory_item_id: int, session: Session):
    inventory_item = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_item_id)).one_or_none()
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory Item not found")
    return inventory_item


#Delete Inventory Item by ID
def delete_inventory_item_by_id(inventory_item_id: int, session: Session):
    # Step 1: Get the Inventory Item by ID
    inventory_item = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_item_id)).one_or_none()
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory Item not found")
    #Step 2: Delete the Inventory Item
    session.delete(inventory_item)
    session.commit()
    return {"message": "Inventory Item Deleted Successfully"}


# Update item by ID
def update_item_by_id(item_id: int, to_update_item_data:InventoryItemUpdate, session: Session):
    # Step 1: Get the Product by ID
    logging.info("Crud Started...")
    inventory_item = session.get(InventoryItem,item_id)
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Update the Product
    dict_data = to_update_item_data.model_dump(exclude_unset=True)
    update_data = {k: v for k, v in dict_data.items() if v is not None}
    logging.info(f"Unique Data: {update_data}")

    # Update inventory_item using the filtered data
    for key, value in update_data.items():
        setattr(inventory_item, key, value)

    session.add(inventory_item)
    session.commit()
    session.refresh(inventory_item)
    return {"message":"Product Updated Successfully"} 

#Get quantity value 
def get_quantity_value(product_id: int, session: Session):
    # Step 1: Get the Inventory Item by product_id
    inventory_item = session.exec(select(InventoryItem).where(InventoryItem.product_id == product_id)).one_or_none()
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory Item not found")
    real_quantity = inventory_item.quantity
    return real_quantity

# Decrease Inventory stock quantity
def decrease_quantity_value(product_id: int, quantity_value: int, session: Session):
    # Fetch the inventory item with the specified product_id
    statement = select(InventoryItem).where(InventoryItem.product_id == product_id)
    result = session.exec(statement)
    inventory_item = result.one_or_none()  # Get the single result or None if no result

    if inventory_item is None:
        raise ValueError(f"No inventory item found with product_id {product_id}")

    # Update the quantity
    updated_quantity = inventory_item.quantity - quantity_value
    inventory_item.quantity = updated_quantity

    # Add the updated item to the session and commit the transaction
    session.add(inventory_item)
    session.commit()
    session.refresh(inventory_item)
    return updated_quantity