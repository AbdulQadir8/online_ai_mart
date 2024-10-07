from fastapi.testclient import TestClient
from app.models.order_model import Order
from app.crud.order_crud import add_new_order

def test_read_root(client: TestClient) ->None:
    response = client.get("http://order-service:8007/")
    assert response.status_code == 200
    assert response.json() == {"Hellow": "Order Service"}



# Test function for the create_order route

def test_create_order(client: TestClient):
    # Set up the mocked return values for dependencies
  
    order_data = {
    "user_id":12,
    "status": "pending",
    "total_amount": 200.00,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "items": [
        {
            "product_id": 1,
            "quantity": 2,
            "price": 50.00
        },
        {
            "product_id": 2,
            "quantity": 1,
            "price": 100.00
        }
    ]
}

    # Make a POST request to the /order/ route using TestClient
    response = client.post("http://order-service:8007/order/", json=order_data)

    # Assertions for the response
    assert response.status_code == 200
    assert response.json() == order_data


def test_read_orders(client: TestClient):
    response = client.get("http://order-service:8007/orders/")
    assert response.status_code == 200
    orders = response.json()
    print(orders)
    assert len(orders) > 1

def test_get_single_order(client: TestClient, db: dict[str, str]):
    user_id = 3
    status = "Processing"
    total_amount = 100
    order_in = Order(user_id=user_id,status=status,total_amount=total_amount)
    order = add_new_order(order=order_in,session=db)
    order_id = order.id
    response = client.get(f"http://order-service:8007/order/{order_id}")
    order_data = response.json()
    assert response.status_code == 200
    assert order_data["id"] == order_id
    assert response.status_code