from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.db_engine import engine
from requests import post, get
from app.core import requests
from app.utils import load_error_json
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login-endpoint")


#Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()



def get_session():
    with Session(engine) as session:
        yield session



def get_current_admin_dep(token: Annotated[str |  None, Depends(oauth2_scheme)]):
    user = requests.get_current_user(token)
    if user.get("is_superuser") == False:
        raise HTTPException(status_code=403, detail="User doesn't have enough privileges")
    return user

GetCurrentAdminDep = Depends(get_current_admin_dep)



def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    auth_token = requests.login_for_access_token(form_data)
    # Make a request to get user data and check if user is admin
    user = requests.get_current_user(auth_token.get("access_token"))
    if user.get("is_superuser") == False:
        raise HTTPException(status_code=403, detail="User doesn't have enough privileges")
    return auth_token

LoginForAccessTokenDep = Annotated[dict, Depends(get_login_for_access_token)]
