# main.py
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator, Annotated, Any
from aiokafka import AIOKafkaConsumer
import asyncio

from app.db_engine import engine
from sqlmodel import SQLModel, Session, select, func
from app.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.utils import create_access_token
from app.models.user_model import User, UserCreate, UserPublic, UsersPublic, UserUpdate, UserRegister, UserUpdateMe,UpdatePassword, Message
from .utils import get_hashed_password, verify_password, decode_token
from app.crud import user_crud
import logging
logging.basicConfig(level=logging.INFO)

# ALGORITHM: str = "HS256"
# SECRET_KEY: str = "Secure Secret Key"

fake_users_db: dict[str, dict[str, str]] = {
    "ameenalam": {
        "username": "ameenalam",
        "full_name": "Ameen Alam",
        "email": "ameenalam@example.com",
        "password": "ameenalamsecret",
    },
    "mjunaid": {
        "username": "mjunaid",
        "full_name": "Muhammad Junaid",
        "email": "mjunaid@example.com",
        "password": "mjunaidsecret",
    },
}

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# loop = asyncio.get_event_loop()
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, 
            title="User Service API with DB", 
            version="0.0.1"
            )

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



@app.get("/")
def read_root():
    return {"App": "User Service1"}

@app.get("/users",dependencies=[Depends(get_current_active_superuser)],response_model=UserPublic)
def ge_all_users(session: SessionDep, skip: int= 0, limit: int= 100) -> Any:
    """
    Retrieve users
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()


    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)

@app.post("/", dependencies=[Depends(get_current_active_superuser)],response_model=UserPublic)
def create_user(*,session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = user_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
    user = user_crud.create_user(session=session, user_create=user_in)
    # if setings.emails_enabled and user_in.email:
    #     email_data = genrate_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
    #     send_email(
    #         email_to=user_in.email,
    #         subject=email_data.subject,
    #         html_content=email_data=html_content,
    #     )
    return user

@app.post("/login")
def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
          session: SessionDep):
    """
    Understanding the login system
    -> Takes form_data that have username and password
    """
    user = session.exec(select(User).where(User.user_name == form_data.username)).one_or_none()
    logging.info(f"(UserData:{user}")

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect Username")
    if verify_password(form_data.password, user.hashed_password) == False:
        raise HTTPException(status_code=400, detail="Incorrect Password")
    
    access_token_expires = timedelta(minutes=1)

    access_token = create_access_token(user.user_name, expires_delta=access_token_expires)

    return {"access_token":access_token, "token_type": "bearer", "expires_in":access_token_expires.total_seconds()}



@app.post("/sign_up", response_model=UserPublic)
def register_user(user_in: UserRegister, session: SessionDep):
    user = user_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = user_crud.create_user(session=session, user_create=user_create)
    return user



@app.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser)-> Any:
    """
    Get current user
    """
    return current_user



@app.patch("/me", response_model=UserPublic)
def update_user_me(session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser)-> Any:
    """
    Update own user
    """
    if user_in.email:
        existing_user = user_crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"

            )
        
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@app.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: int, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User,user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403,
                            detail="User doesn't have enough privileges")
    return user




@app.patch("/me/password", response_model=Message)
def update_password_me(*, session: SessionDep, body: UpdatePassword, current_user: CurrentUser)-> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New Password cannot be the same as the current one"
        )
    hashed_password = get_hashed_password(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password update successfully")


@app.patch("/{user_id}",dependencies=[Depends(get_current_active_superuser)],response_model=UserPublic)
def update_user(*,session: SessionDep, user_id: int, user_in: UserUpdate) -> Any:
    """
    Update a user
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id doesn't exist in the system"
        )
    if user_in.email:
        existing_user = user_crud.get_user_by_email(session=session,email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409,
                                detail="User already exists with this email")
    
    db_user = user_crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@app.delete("/{user_id}")
def delete_user(session: SessionDep, current_user: CurrentUser, user_id:int)-> Message:
    """Delete a user"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    elif user != current_user and not current_user.is_superuser:
        raise HTTPException(status_code=403,
                            detail="The user doesn't have enough privileges"
                            )
    elif user == current_user and current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    # statement = delete(Item).where(col(Item.owner_id) == user_id)
    # session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted Successfully")




@app.get("/decode-token")
def decode_token(token: str):
    try:
        decoded_data = decode_token(token=token)
        logging.info(f"DecodedData:{decoded_data}")
        return decoded_data 
    except JWTError as e:
        return {"error": str(e)}
