from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
from tests.utils.utils import random_email,random_password
from app.models.user_model import UserCreate
from app.crud.user_crud import create_user, authenticate

from app import crud




def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_password()
    user_in =UserCreate(email=email, password=password)
    user = create_user(session=db,user_create=user_in)
    assert user.email == email
    assert hasattr(user,"hashed_password")

def test_authenticate(db: Session) -> None:
    email = random_email()
    password = random_password()
    user_in = UserCreate(email=email, password=password)
    user = create_user(session=db,user_create=user_in)
    authenticated_user = user.authenticate(session=db,email=email,password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email
