import random
import string

from fastapi.testclient import TestClient
from app import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=5))

def random_number() -> str:
    return "".join(random.choices(string.digits, k=4))

def random_password() -> str:
    return f"{random_lower_string()}123@_!$"

def random_email() -> str:
    return f"{random_lower_string()}{random_number()}@gmail.com"

def random_user_name() -> str:
    return f"{random_lower_string()}_09"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {"username": settings.FIRST_SUPERUSER,
                  "password": settings.FIRST_SUPERUSER_PASWORD
                  }
    r = client.post(f"http://user-service:8000/login", data=login_data)
    tokens =r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization":f"Bearer {a_token}"}
    return headers
