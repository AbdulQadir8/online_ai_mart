from fastapi.testclient import TestClient
from app import settings

from sqlmodel import Session, select
from app.models.user_model import UserCreate, User
from tests.utils.utils import random_user_name, random_email,random_password
from app.crud.user_crud import create_user, get_user_by_email
from app.utils import verify_password

def test_read_superuser_me(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    response = client.get("http://user-service:8000/me",
                          headers=superuser_token_headers)
    current_user = response.json() 
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_read_normal_user_me(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    response = client.get("http://user-service:8000/me",
                          headers=normal_user_token_headers)
    current_user = response.json() 
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    data = {"user_name":username,
            "email":email,
            "password":password}
    response = client.post("http://user-service:8000/",
                    headers=superuser_token_headers,
                    json=data)
    user = response.json()
    assert response.status_code == 200
    assert user["email"] == email    

def test_get_existing_user(client: TestClient, superuser_token_headers: dict[str, str],db: Session) -> None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    user = create_user(session=db, user_create=user_in)
    user_id = user.id
    response = client.get(f"http://user-service:8000/{user_id}",
                           headers=superuser_token_headers)
    user_data = response.json()
    assert response.status_code == 200
    assert user_data["email"] == email

def test_get_existing_current_user(client: TestClient, db: Session):
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    user = create_user(session=db,user_create=user_in)
    user_id = user.id

    login_data = {"username":username,
                  "password":password}
    r = client.post("http://user-service:8000/login",
                           data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization":f"Bearer {a_token}"}
    r = client.get(f"http://user-service:8000/{user_id}",
                   headers=headers)
    api_user = r.json()
    assert r.status_code == 200
    existing_user = get_user_by_email(session=db, email=email)
    assert existing_user
    assert existing_user.email == api_user["email"]

def test_get_existing_user_permissions_error(client: TestClient, normal_user_token_headers: dict[str,str]) ->None:
    r = client.get("http://user-service:8000/99999",
                   headers=normal_user_token_headers)
    assert r.status_code == 403
    assert r.json() == {"detail":"User doesn't have enough privileges"}

def test_create_user_exsiting_username(client: TestClient, db: Session,
                                       superuser_token_headers: dict[str, str]) ->None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    create_user(session=db,user_create=user_in)
    data = {"user_name":username,
            "email":email,
            "password":password}
    r = client.post("http://user-service:8000/",
                headers=superuser_token_headers,
                json=data)
    created_user = r.json()
    assert r.status_code == 400
    assert "id" not in created_user

def test_create_user_by_normal_user(client:TestClient, normal_user_token_headers: dict[str,str]) ->None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    data = {"user_name":username,
            "email":email,
            "password":password}
    r = client.post("http://user-service:8000/",
                    headers=normal_user_token_headers,
                    json=data)
    assert r.status_code == 400

def test_retrieve_users(client: TestClient, db: Session, superuser_token_headers: dict[str,str]) ->None:
    username1 = random_user_name()
    email1 = random_email()
    password1 = random_password()
    user_in1 = UserCreate(user_name=username1,email=email1,password=password1)
    username2 = random_user_name()
    email2 = random_user_name()
    password2 = random_password()
    user_in2 = UserCreate(user_name=username2,email=email2,password=password2)
    create_user(session=db,user_create=user_in1)
    create_user(session=db,user_create=user_in2)
 
    r = client.get("http://user-service:8000/users",
               headers=superuser_token_headers)
    all_users = r.json()
    assert r.status_code == 200
    assert  len(all_users) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item 

def test_update_user_me(client: TestClient, normal_user_token_headers: dict[str,str], db: Session) -> None:
    full_name = "Updated Name"
    email = random_email()
    data = {"full_name":full_name,"email":email}
    r = client.patch("http://user-service:8000/update/me",
                headers=normal_user_token_headers,
                json=data)
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["full_name"] == full_name
    assert updated_user["email"] == email

    user_query = select(User).where(User.email == email)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == email
    assert user_db.full_name == full_name

def test_update_password_me(client: TestClient, superuser_token_headers: dict[str, str], db: Session) ->None:
    new_password = random_password()
    data = {
        "current_password":settings.FIRST_SUPERUSER_PASWORD,
        "new_password":new_password
    }
    r = client.patch("http://user-service:8000/me/password",
                     headers=superuser_token_headers,
                     json=data)
    r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == settings.FIRST_SUPERUSER
    assert verify_password(new_password, user_db.hashed_password)

    # Revert to the old password to keep consistency in test
    old_data = {
        "current_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASWORD,
    }
    r = client.patch(
        "http://user-service:8000/me/password",
        headers=superuser_token_headers,
        json=old_data,
    )
    db.refresh(user_db)

    assert r.status_code == 200
    assert verify_password(settings.FIRST_SUPERUSER_PASWORD, user_db.hashed_password)


def test_update_password_me_incorrect_password_me(client: TestClient, superuser_token_headers: dict[str, str]) ->None:
    new_password = random_password()
    old_data = {
        "current_password":new_password,
        "new_password":new_password
    }
    r = client.patch("http://user-service:8000/me/password",
                 headers=superuser_token_headers,
                 json=old_data)
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"
    
def test_update_user_me_email_exists(client: TestClient,db: Session, normal_user_token_headers: dict[str, str]) ->None:
    username = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=username,email=email,password=password)
    user = create_user(session=db,user_create=user_in)

    old_data = {"email":user.email}

    r = client.patch("http://user-service:8000/update/me",
                 headers=normal_user_token_headers,
                 json=old_data)
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"

def test_update_password_me_same_password_error(client: TestClient, db: Session, superuser_token_headers: dict[str,str]) ->None:
    data = {
        "current_password":settings.FIRST_SUPERUSER_PASWORD,
        "new_password":settings.FIRST_SUPERUSER_PASWORD
    }
    r = client.patch("http://user-service:8000/me/password",
                 headers=superuser_token_headers,
                 json=data)
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "New Password cannot be the same as the current one" 

# def test_register_user(client: TestClient, db: Session) -> None:
#     email = random_email()
#     full_name = random_user_name()
#     password = random_password()
#     data = {"email": email, "password": password, "full_name": full_name}
#     r = client.post(
#         "http://user-service:8000/sign_up",
#         json=data,
#     )
#     assert r.status_code == 200
#     created_user = r.json()
#     assert created_user["email"] == email
#     assert created_user["full_name"] == full_name

#     user_query = select(User).where(User.email == email)
#     user_db = db.exec(user_query).first()
#     assert user_db
#     assert user_db.email == email
#     assert user_db.full_name == full_name
#     assert verify_password(password, user_db.hashed_password)


def test_register_user_already_exists_error(client: TestClient) ->None:
    password = random_password()
    full_name = random_user_name()
    data = {"email":settings.FIRST_SUPERUSER,
            "password":password,
            "full_name":full_name}
    r = client.post("http://user-service:8000/sign_up",
                json=data)
    assert r.status_code == 400
    user_data = r.json()
    assert user_data["detail"] == "The user with this email already exists in the system"

def test_update_user(client: TestClient,db: Session,superuser_token_headers: dict[str,str]) ->None:
    user_name = random_user_name()
    email = random_email()
    password = random_password()
    user_in = UserCreate(user_name=user_name,email=email,password=password)
    user = create_user(session=db,user_create=user_in)
    user_id = user.id

    data = {"full_name":"Update Name"}
    r = client.patch(f"http://user-service:8000/{user_id}",
                 headers=superuser_token_headers,
                 json=data)
    updated_user = r.json()
    assert r.status_code == 200
    assert updated_user["full_name"] == "Update Name"

    query = select(User).where(User.email == email)
    db_user = db.exec(query).first()
    
    db.refresh(db_user)
    assert db_user
    assert db_user.full_name == "Update Name"

def test_update_user_not_exists(client: TestClient, superuser_token_headers: dict[str,str]):
    data = {"full_name":"Update Name"}
    r = client.patch(f"http://user-service:8000/99999",
                 headers=superuser_token_headers,
                 json=data)
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id doesn't exist in the system"

def test_update_user_email_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    username1 = random_user_name()
    email1 = random_email()
    password1 = random_password()
    user_in1 = UserCreate(user_name=username1,email=email1,password=password1)
    username2 = random_user_name()
    email2 = random_user_name()
    password2 = random_password()
    user_in2 = UserCreate(user_name=username2,email=email2,password=password2)
    user1 = create_user(session=db,user_create=user_in1)
    user2 = create_user(session=db,user_create=user_in2)

    data = {"email": user2.email}
    r = client.patch(
        f"http://user-service:8000/{user1.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User already exists with this email"