# main.py
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator, Annotated
from aiokafka import AIOKafkaConsumer
import asyncio

from app.db_engine import engine
from sqlmodel import SQLModel, Session
from app.deps import get_kafka_producer, get_session
from app.utils import create_access_token
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALGORITHM: str = "HS256"
SECRET_KEY: str = "Secure Secret Key"

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



@app.get("/")
def read_root():
    return {"App": "User Service"}

@app.post("/login")
def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
          session: Annotated[Session, Depends(get_session)]):
    """
    Understanding the login system
    -> Takes form_data that have username and password
    """
    user_in_fake_db = fake_users_db.get(form_data.username)

    if not user_in_fake_db:
        raise HTTPException(status=400, detail="Incorrect Username")
    if not form_data.password == user_in_fake_db["password"]:
        raise HTTPException(status_code=400, detail="Incorrect Password")
    
    access_token_expires = timedelta(minutes=1)

    access_token = create_access_token(user_in_fake_db["username"], expires_delta=access_token_expires)

    return {"access_token":access_token, "token_type": "bearer", "expires_in":access_token_expires.total_seconds()}


@app.get("/secial-items")
def get_items(token: Annotated[str, Depends(oauth2_scheme)]):
    decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
    return {"Special":"Items",
            "decoded_token": decoded_token_data}


@app.get("/get-token")
def get_token(name: str):
    access_token_expiry_minutes = timedelta(minutes=1)

    print("access_token_expiry_minutes",access_token_expiry_minutes)

    genrated_token = create_access_token(
        subject=name, expires_delta=access_token_expiry_minutes
    )
    return {"access_token: ", genrated_token}


@app.get("/decode-token")
def decode_token(token: str):
    try:
        decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
        return {"decoded_token": decoded_token_data}
    except JWTError as e:
        return {"error": str(e)}


@app.post("/register_user")
def register_user(user: User, session: Annotated[Session, Depends(get_session)]):
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@app.get("/get_products")
def get_products(token: Annotated[str, Depends(oauth2_scheme)]):
    decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
    return {"All":"Products",
            "Token":decoded_token_data}