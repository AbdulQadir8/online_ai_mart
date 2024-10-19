from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    response = client.get("http://payment-service:8008")
    assert response.status_code == 200
    assert response.json() == {"App": "Payment Service"}

def test_create_payment_endpoint(client: TestClient):
    data = {
        "order_id": 2,
        "user_id": 2,
        "amount": 200,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response.json()
    assert response.status_code == 200
    assert created_payment["amount"] == 200
    assert created_payment["currency"] == "usd"
    assert created_payment["status"] == "pending"


def test_get_payment_endpoint(client: TestClient):
    data = {
        "order_id": 3,
        "user_id": 3,
        "amount": 300,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    payment_id = created_payment["id"]
    response2 = client.get(f"http://payment-service:8008/payments/{payment_id}")
    retrieved_payment = response2.json()
    assert response2.status_code == 200
    assert retrieved_payment
    assert retrieved_payment["amount"] == 300
    assert retrieved_payment["user_id"] == 3

def test_get_payment_endpoint_not_found(client: TestClient):
    payment_id = 99999
    response2 = client.get(f"http://payment-service:8008/payments/{payment_id}")
    assert response2.status_code == 404
    assert response2.json()["detail"] == "Payment not found"

def test_update_payment_status_endpoint(client: TestClient):
    data = {
        "order_id": 4,
        "user_id": 4,
        "amount": 400,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    payment_id = created_payment["id"]
    status = {"status":"completed"}
    response = client.patch(f"http://payment-service:8008/payments/{payment_id}",
                 json=status)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"