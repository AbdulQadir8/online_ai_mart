from sqlmodel import Session

from app.crud.inventory_crud import (add_new_inventory_item,
                                     get_all_inventory_items,
                                     get_inventory_item_by_id,
                                     delete_inventory_item_by_id,
                                     update_item_by_id,
                                     get_quantity_value,
                                     decrease_quantity_value)
from app.models.inventory_model import CreateInventoryItem,InventoryItemUpdate


def test_add_new_inventory_item(db: Session):
    inventory_in = CreateInventoryItem(product_id=1,
                                      variant_id=2,
                                      quantity=40,
                                      status="in_stock")
    new_inventory = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    assert new_inventory.product_id == 1
    assert new_inventory.quantity == 40 

def test_get_all_inventory_items(db: Session):
    inventory_in1 = CreateInventoryItem(product_id=2,
                                  variant_id=5,
                                  quantity=56,
                                  status="in_stock")
    inventory_in2 = CreateInventoryItem(product_id=3,
                               variant_id=6,
                               quantity=88,
                               status="in_stock")
    add_new_inventory_item(inventory_item_data=inventory_in1, session=db)
    add_new_inventory_item(inventory_item_data=inventory_in2, session=db)
    inventory_items = get_all_inventory_items(session=db)
    assert len(inventory_items) > 1
    for item in inventory_items:
        if item.id == 2:
            assert item.quantity == 88


def test_get_inventory_item_by_id(db: Session):
    inventory_in = CreateInventoryItem(product_id=8,
                           variant_id=7,
                           quantity=98,
                           status="in_stock")
    created_inventory = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    inventory_id = created_inventory.id
    db_inventory = get_inventory_item_by_id(inventory_item_id=inventory_id,session=db)
    assert db_inventory.variant_id == 7
    assert db_inventory.quantity == 98

def test_get_inventory_item_by_id_not_found(db: Session):
    inventory_id = 99999
    db_inventory = get_inventory_item_by_id(inventory_item_id=inventory_id,session=db)
    assert db_inventory == None

def test_delete_inventory_item_by_id(db: Session):
    inventory_in = CreateInventoryItem(product_id=4,
                      variant_id=5,
                      quantity=66,
                      status="in_stock")
    created_inventory = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    inventory_id = created_inventory.id
    db_inventory = delete_inventory_item_by_id(inventory_item_id=inventory_id,session=db)
    assert db_inventory == {"message": "Inventory Item Deleted Successfully"}

def test_delete_inventory_item_by_id_not_found(db: Session):
    inventory_id = 99999
    db_inventory = delete_inventory_item_by_id(inventory_item_id=inventory_id,session=db)
    assert db_inventory == None

def test_update_item_by_id(db: Session):
    inventory_in = CreateInventoryItem(product_id=5,
                   variant_id=6,
                   quantity=62,
                   status="in_stock")
    created_inventory = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    inventory_id = created_inventory.id
    new_data = InventoryItemUpdate(quantity=90)
    updated_inventory_item = update_item_by_id(item_id=inventory_id,to_update_item_data=new_data,session=db)
    db_inventory_item = get_inventory_item_by_id(inventory_item_id=inventory_id, session=db)
    assert db_inventory_item.quantity == 90
    assert updated_inventory_item == {"message":"Product Updated Successfully"} 

def test_update_item_by_id_not_found(db: Session):
    inventory_id = 99999
    new_data = InventoryItemUpdate(quantity=90)
    updated_inventory_item = update_item_by_id(item_id=inventory_id,to_update_item_data=new_data,session=db)
    assert updated_inventory_item == None

def test_get_quantity_value(db: Session):
    inventory_in = CreateInventoryItem(product_id=10,
               variant_id=7,
               quantity=70,
               status="in_stock")
    created_inventory = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    productid = created_inventory.product_id
    db_quantity = get_quantity_value(product_id=productid, session=db)
    assert db_quantity == 70


def test_get_quantity_value_not_found(db: Session):
    product_id = 99999
    db_quantity = get_quantity_value(product_id=product_id, session=db)
    assert db_quantity == None

def test_decrease_quantity_value(db: Session):
    inventory_in = CreateInventoryItem(product_id=11,
           variant_id=7,
           quantity=100,
           status="in_stock")
    created_inventory = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    productid = created_inventory.product_id
    updated_quantity = decrease_quantity_value(product_id=productid,quantity_value=2,session=db)
    assert updated_quantity == 98

def test_decrease_quantity_value_not_found(db: Session):
    productid = 99999
    updated_quantity = decrease_quantity_value(product_id=productid,quantity_value=2,session=db)
    assert updated_quantity == None