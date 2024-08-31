from typing import Annotated
from fastapi import Depends, HTTPException, status
from aiokafka import AIOKafkaProducer
from sqlmodel import Session, select
from .models.user_model import User, TokenPayload
from app.db_engine import engine
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
# Kafka Producer as a dependency
from app.utils import ALGORITHM, SECRET_KEY, decode_token
import logging
logging.basicConfig(level=logging.INFO)



reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="login"
)



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




SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[Session, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep)-> User:
    try:
        payload = decode_token(token=token)
        logging.info(f"PayLoad Data:{payload}")
        token_data = TokenPayload(**payload)
        print(f"TokenData :{token_data}")

    except JWTError as jwt_error:
        print(f"JWT Error: {jwt_error}")  # Log the JWT error
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It is Forbidden"
        )
    except ValidationError as val_error:
        print(f"Validation Error: {val_error}")  # Log the validation error
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It is Forbidden"
        )
    user = session.exec(select(User).where(User.user_name == token_data.sub)).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User not Found:{token_data.sub}")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser)-> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user