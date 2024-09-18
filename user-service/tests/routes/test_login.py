from app import settings
from fastapi.


def test_access_token(client: TestClient) -> None:
    login_data = {
        "username":settings.FIRST_SUPERUSER,
        "password":settings.FIRST_SUPERUSER_PASWORD
    }
    r = client.post(f"http://127.0.0.1:8009/login/access-token",data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]

def test_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password":"incorrect"
    }