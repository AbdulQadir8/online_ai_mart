from fastapi.testclient import TestClient

from tests.conftest import get_current_admin_dep

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
    data = {"status":"completed"}
    response = client.patch(f"http://payment-service:8008/payments/{payment_id}",
                            json=data)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_update_payment_status_endpoint_not_found(client: TestClient):
    payment_id = 99999
    data = {"status":"Processing"}
    response = client.patch(f"http://payment-service:8008/payments/{payment_id}",
                 json=data)
    assert response.status_code == 404

def test_delete_payment_by_id(client: TestClient):
    data = {
        "order_id": 5,
        "user_id": 5,
        "amount": 500,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    payment_id = created_payment["id"]
    response = client.delete(f"http://payment-service:8008/payments/{payment_id}")
    assert response.status_code == 200
    assert response.json() == {"message":"Payment deleted successfully"}

def test_delete_payment_by_id_not_found(client: TestClient):
    payment_id = 999999
    response = client.delete(f"http://payment-service:8008/payments/{payment_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

def test_create_transaction_endpoint(client: TestClient):
    data = {
        "order_id": 7,
        "user_id": 7,
        "amount": 700,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    data = {
            "status": "initiated",
            "payment_id": created_payment["id"]
            }
    response2 = client.post("http://payment-service:8008/transactions/",
                           json=data)
    assert response2.status_code == 200
    assert response2.json()["status"] == "initiated"
    assert response2.json()["payment_id"] == created_payment["id"]

def test_get_transaction_endpoint(client: TestClient):
    data = {
        "order_id": 7,
        "user_id": 7,
        "amount": 700,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    data = {
            "status": "initiated",
            "payment_id": created_payment["id"]
            }
    response2 = client.post("http://payment-service:8008/transactions/",
                           json=data)
    transaction_id = response2.json()["id"]
    
    response3 = client.get(f"http://payment-service:8008/transactions/{transaction_id}")
    assert response3.status_code == 200
    assert response3.json()["status"] == "initiated"

def test_get_transaction_endpoint_not_found(client: TestClient):
    transaction_id = 99999
    response = client.get(f"http://payment-service:8008/transactions/{transaction_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"

def test_update_transaction_status_endpoint(client: TestClient):
    data = {
        "order_id": 8,
        "user_id": 8,
        "amount": 800,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    data = {
            "status": "initiated",
            "payment_id": created_payment["id"]
            }
    response2 = client.post("http://payment-service:8008/transactions/",
                           json=data)
    transaction_id = response2.json()["id"]

    data = {"status":"Failed"}

    response3 = client.patch(f"http://payment-service:8008/transactions/{transaction_id}",
                     json=data)
    returned_data = response3.json()
    assert response3.status_code == 200
    assert returned_data["status"] == "Failed"

def test_update_transaction_status_endpoint_not_found(client: TestClient):
    transaction_id = 99999
    data = {"status":"Failed"}
    response = client.patch(f"http://payment-service:8008/transactions/{transaction_id}",
                     json=data)
    returned_data = response.json()
    assert response.status_code == 404
    assert returned_data['detail'] == "Transaction not found"

def test_delete_transaction_by_id(client: TestClient):
    data = {
        "order_id": 9,
        "user_id": 9,
        "amount": 900,
        "currency": "usd",
        "status": "pending",
        "stripe_checkout_session_id": "string"
        }

    response1 = client.post("http://payment-service:8008/payments/",
                           json=data)
    created_payment = response1.json()
    data = {
            "status": "initiated",
            "payment_id": created_payment["id"]
            }
    response2 = client.post("http://payment-service:8008/transactions/",
                           json=data)
    transaction_id = response2.json()["id"]
    
    response3 = client.delete(f"http://payment-service:8008/transaction/{transaction_id}")
    assert response3.status_code == 200
    assert response3.json() == {"message":"Transaction deleted successfully"}


def test_delete_transaction_by_id_not_found(client: TestClient):
    transaction_id = 99999
    response3 = client.delete(f"http://payment-service:8008/transaction/{transaction_id}")
    assert response3.status_code == 404
    assert response3.json()["detail"] == "Transaction not found"


# def test_create_checkout_session(client: TestClient):
#     data = {
#         "order_id": 2,
#         "user_id": 2,
#         "amount": 200,
#         "currency": "usd",
#         "status": "pending",
#         "stripe_checkout_session_id": "string"
#         }

#     response = client.post("http://payment-service:8008/payments/",
#                            json=data)
#     created_payment = response.json()
#     payment_id = created_payment["id"]
#     response = client.post(f"http://payment-service:8008/create-checkout-session/{payment_id}")
#     assert response.status_code == 200