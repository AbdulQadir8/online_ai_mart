from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.inventory_model import CreateInventoryItem
from app.crud.inventory_crud import add_new_inventory_item


def test_create_new_inventory_item(client: TestClient):
    inventory_in = {"product_id":3,
                    "variant_id":2,
                    "quantity":55,
                    "status":"in_stock"}
    response = client.post("http://inventory-serivce/manage-inventory/",json=inventory_in)
    assert response.status_code == 200
    assert response.json() == inventory_in

def test_all_inventory_items(client: TestClient, db: TestClient):
    inventory_in1 = {"product_id":4,
                "variant_id":5,
                "quantity":77,
                "status":"in_stock"}
    inventory_in2 = {"product_id":6,
                "variant_id":8,
                "quantity":76,
                "status":"in_stock"}
    add_new_inventory_item(inventory_item_data=inventory_in1, session=db)
    add_new_inventory_item(inventory_item_data=inventory_in2, session=db)
    response = client.get("http://inventory-serivce/manage-inventory/all")
    items = response.json()
    assert response.status_code == 200
    assert len(items) > 1

def test_single_inventory_item(client: TestClient, db: Session):
    inventory_in = {"product_id":33,
                "variant_id":3,
                "quantity":62,
                "status":"in_stock"}
    new_item = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    item_id = new_item.id
    response = client.get(f"http://inventory-serivce/manage-inventory/{item_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["quantity"] == 62

def test_single_inventory_item_not_found(client: TestClient, db: Session):
    item_id = 99999
    response = client.get(f"http://inventory-serivce/manage-inventory/{item_id}")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == f"Inventory not found with id:{item_id}"

def test_delete_single_inventory_item(client: TestClient, db: Session):
    inventory_in = {"product_id":20,
                "variant_id":4,
                "quantity":74,
                "status":"in_stock"}
    new_item = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    item_id = new_item.id
    response = client.delete(f"http://inventory-serivce/manage-inventory/{item_id}")
    data = response.json()
    assert response.status_code == 200
    assert data == {"status":"Inventory deleted Successfully"}

def test_delete_single_inventory_item_not_found(client: TestClient, db: Session):
    item_id = 99999
    response = client.delete(f"http://inventory-serivce/manage-inventory/{item_id}")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == f"Inventory not found with id:{item_id}"

def test_update_single_inventoryitem(client: TestClient, db: Session):
    inventory_in = {"product_id":21,
                "variant_id":7,
                "quantity":53,
                "status":"in_stock"}
    new_item = add_new_inventory_item(inventory_item_data=inventory_in, session=db)
    item_id = new_item.id
    data = {"quantity":0,
            "status":"out_of_stock"}
    response = client.patch(f"http://inventory-serivce/manage-inventory/{item_id}",
                            json=data)
    r_data = response.json()
    assert response.status_code == 200
    assert r_data["status"] == "out_of_stock"

def test_update_single_inventoryitem_not_found(client: TestClient, db: Session):
    item_id = 99999
    data = {"quantity":0,
            "status":"out_of_stock"}
    response = client.patch(f"http://inventory-serivce/manage-inventory/{item_id}",
                            json=data)
    r_data = response.json()
    assert response.status_code == 404
    assert r_data["detail"] == f"Inventory not found with id:{item_id}"