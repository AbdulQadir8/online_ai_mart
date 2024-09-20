from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
from tests.utils.utils import random_email,random_password,random_user_name
from app.models.user_model import UserCreate, User, UserUpdate
from app.crud.user_crud import create_user, authenticate, update_user
from app.utils import verify_password, get_hashed_password



def test_create_user(db: Session) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in =UserCreate(user_name=username,email=email, password=password)
    user = create_user(session=db,user_create=user_in)
    assert user.email == email
    assert hasattr(user,"hashed_password")

def test_authenticate_user(db: Session) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email, password=password)
    user = create_user(session=db,user_create=user_in)
    authenticated_user = authenticate(session=db,email=email,password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email

def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_password()
    user = authenticate(session=db, email=email,password=password)
    assert user is None

def test_check_if_user_is_activate(db: Session) -> None:
    username = random_user_name()
    email=random_email()
    password=random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    user = create_user(session=db,user_create=user_in)
    assert user.is_active is True

def test_check_if_user_is_active_inactive(db: Session) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password, disabled=True)
    user = create_user(session=db, user_create=user_in)
    assert user.is_active

def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password,is_superuser=True)
    user = create_user(session=db,user_create=user_in)
    assert user.is_superuser is True

def test_check_if_user_is_normal_user(db: Session) -> None:
    username = random_user_name()
    email= random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    user = create_user(session=db,user_create=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    user = create_user(session=db,user_create=user_in)
    user_2 = db.get(User,user.id)
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)

def test_update_user(db: Session) -> None:
    username = random_user_name()
    password = random_password()
    email = random_email()
    user_in = UserCreate(user_name=username,email=email, password=password)
    user = create_user(session=db, user_create=user_in)
    new_password = random_password()
    hashed_password = get_hashed_password(new_password)
    user_in_update = UserUpdate(password=hashed_password)
    if user.id is not None:
        update_user(session=db, db_user=user, user_in=user_in_update)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
