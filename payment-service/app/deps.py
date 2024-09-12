from aiokafka import AIOKafkaProducer
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlmodel import Session
from app.db_engine import engine
from app import requests

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-endpoint")


# Kafka Producer as a dependency
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