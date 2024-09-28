from fastapi.testclient import TestClient
from sqlmodel import Session


from tests.utils.utils import random_email, random_password,random_user_name
from app.crud.user_crud import create_user, get_user_by_email, update_user
from app.models.user_model import UserCreate, User, UserUpdate

def user_authentication_headers(
        *, client: TestClient, username:str, password: str
) -> dict[str,str]:
    data = {"username":username, "password": password}

    r = client.post(f"http://user-service:8000/login",data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization":f"Bearer {auth_token}"}
    return headers

def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_password()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    username = random_user_name()
    password = random_password()
    user = get_user_by_email(session=db, email=email)
    if not user:
        user_in_create = UserCreate(user_name=username,email=email,password=password)
        user = create_user(session=db, user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        if not user.id:
            raise Exception("User Id not set")
        user = update_user(session=db, db_user=user, user_in=user_in_update)
    
    return user_authentication_headers(client=client, username=username, password=password)
