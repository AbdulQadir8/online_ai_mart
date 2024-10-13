from fastapi.testclient import TestClient
import logging
from sqlmodel import Session
from app.models.product_model import CreateProduct
from app.crud.product_crud import add_new_product
logging.basicConfig(level=logging.INFO)

# Define your test function
def test_create_new_product(client: TestClient):
    # Mock input product data
    product_data = {
        "name": "Test Product",
        "description":"This is test product",
        "price": 100,
        "expiry": "2024-10-12",
        "category": "Medium"
    }
    
    response = client.post("http://product-service:8005/manage-products/", json=product_data)
    
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"

def test_call_all_products(client: TestClient, db: Session):
    product1 = CreateProduct(name="Laptop",
                            description="This is Laptop",
                            price=900,
                            category="6th Genration")
    product2 = CreateProduct(name="Mouse",
                            description="This is Mouse",
                            price=300,
                            category="Medium")
    add_new_product(product_data=product1,session=db)
    add_new_product(product_data=product2,session=db)

    response = client.get("http://product-service:8005/manage-products/all")
    products = response.json()
    logging.info(f"PRODUCTS: {products}")
    assert response.status_code == 200
    assert len(products) > 1

def test_get_single_product(client: TestClient, db: Session):
   product_in = CreateProduct(name="Knife",
                           description="This is Knife",
                           price=150,
                           category="Medium")
   product = add_new_product(product_data=product_in,session=db)
   product_id = product.id
   response = client.get(f"http://product-service:8005/manage-products/{product_id}")
   data = response.json()
   assert response.status_code == 200
   assert data["name"] == "Knife"

def test_get_single_product_not_found(client: TestClient):
   product_id = 99999
   response = client.get(f"http://product-service:8005/manage-products/{product_id}")
   data = response.json()
   assert response.status_code == 400
   assert data["detail"] == "Product not found"

def test_delete_single_product(client: TestClient, db: Session):
    product_in = CreateProduct(name="Cap",
                        description="This is cap",
                        price=440,
                        category="Casual")
    product = add_new_product(product_data=product_in,session=db)
    product_id = product.id
    response = client.delete(f"http://product-service:8005/manage-products/{product_id}")
    data = response.json()
    assert response.status_code == 200
    assert data == {"status": "Product deleted successfully"}

def test_delete_single_product_not_found(client: TestClient, db: Session):
    product_id = 99999
    response = client.delete(f"http://product-service:8005/manage-products/{product_id}")
    data = response.json()
    assert response.status_code == 400
    assert data["detail"] == f"Product not found with this {product_id}"


def test_update_single_product(client: TestClient, db: Session):
     product_in = CreateProduct(name="Scissor",
                     description="This is Scissor",
                     price=200,
                     category="Normal")
     product = add_new_product(product_data=product_in,session=db)
     product_id = product.id
     data = {"category":"Medium"}
     response = client.patch(f"http://product-service:8005/manage-products/{product_id}",
                             json=data)
     assert response.status_code == 200
     assert response.json() == {"message":"Product Updated Successfully"}

def test_test_update_single_product_not_found(client: TestClient, db: Session):
    product_id = 99999
    data = {"category":"Medium"}
    response = client.patch(f"http://product-service:8005/manage-products/{product_id}",
                            json=data)
    data = response.json()
    assert response.status_code == 400
    assert data["detail"] == f"Product not found with this {product_id}"