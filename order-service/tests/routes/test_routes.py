from fastapi.testclient import TestClient
from app import settings
import requests

from sqlmodel import Session, select


def test_read_root(client: TestClient) ->None:
    response = client.get("http://order-service:8007/")
    assert response.status_code == 200
    assert response.json() == {"Hellow": "Order Service"}

def test_create_order(client: TestClient,
                      normal_user_token_headers: dict[str, str]) ->None:
    data={"email":settings.EMAIL_TEST_USER,
          "password":"test_password"}
    response = requests.post("http://user-service:8009/sign_up",json=data)
    assert response.status_code == 200