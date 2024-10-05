from fastapi.testclient import TestClient
from sqlmodel import Session
import requests 


from tests.utils.utils import random_email, random_password,random_user_name


def user_authentication_headers(
        *, client: TestClient, username:str, password: str
) -> dict[str,str]:
    data = {"username":username, "password": password}

    r = requests.post(f"http://user-service:8000/login",data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization":f"Bearer {auth_token}"}
    return headers


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    email = random_email()
    user_name = random_user_name()
    password = random_password()
    data = {"email": email, "password": password, "user_name": user_name}
    r = requests.post(
        "http://user-service:8000/sign_up",
        json=data,
    )
    created_user = r.json()
    print(f"User Data:{created_user}")
    assert r.status_code == 200

    return user_authentication_headers(client=client, username=created_user["user_name"], password=password)
