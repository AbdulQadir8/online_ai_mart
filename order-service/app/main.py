# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
from app.db_engine import engine
import asyncio
import json
from app.deps import get_kafka_producer, get_session, custom_json_serializer
from app.models.order_model import CreateOrder, Order, OrderItem, UpdateOrder, UpdateItem, OrderItem
from app.consumers.order_consumer import consume_messages
from app.crud.order_crud import get_single_order, add_new_order
from app.requests import get_current_user, login_for_access_token
import logging
logging.basicConfig(level=logging.INFO)

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
    task = asyncio.create_task(consume_messages('InventoryReserved', 'broker:19092'))
    yield



app = FastAPI(
     lifespan=lifespan, 
     title="Hello World API with DB", 
     version="0.0.1",
     servers=[
        {
            "url": "http://127.0.0.1:8007", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        },{
            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-endpoint")


@app.get("/")
def read_root():
    return {"Hellow": "Order Service"}

@app.post("/login-endpoint", tags=["Wrapper Auth"])
def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
    auth_token = login_for_access_token(form_data)
    return auth_token

@app.post("/order/")
async def create_order(order_data: CreateOrder,
                       session: Annotated[Session, Depends(get_session)],
                       producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
                       user_data: Annotated[str | None, Depends(get_current_user)]):
    """ Create a new inventory item and send it to Kafka"""
      
    # Convert order_data to a dictionary and handle datetime fields
    order_dict = order_data.dict()
    order_dict["user_id"] = user_data["id"]
    order_dict["user_email"] = user_data["email"]
    order_dict["created_at"] = order_data.created_at.isoformat()
    order_dict["updated_at"] = order_data.updated_at.isoformat()
    logging.info(f"OrderDict:{order_dict}")
    order_json = json.dumps(order_dict).encode("utf-8")
    print(f"Order Json: {order_json}")
    #Produce Message
    await producer.send_and_wait("order_events",order_json)
    return order_data

 

@app.get("/orders/", response_model=list[Order])
def read_orders(session: Annotated[Session, Depends(get_session)],
                user_data: Annotated[str | None, Depends(get_current_user)]):
        orders = session.exec(select(Order).where(Order.user_id == user_data["id"])).all()
        return orders


@app.get("/order/{order_id}")
def get_order_by_id(order_id:int, 
                    session: Annotated[Session, Depends(get_session)],
                    user_data: Annotated[str | None, Depends(get_current_user)]):
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return order

@app.get("/orderitem/{order_id}")
def get_order_and_item_by_id(order_id:int, 
                             session: Annotated[Session, Depends(get_session)],
                             user_data: Annotated[str | None, Depends(get_current_user)]):
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return order

    return {"Order":order,
            "OrderItem":order.items}

@app.get("/orderitem/{order_id}")
def orderitem_by_orderid(order_id:int, 
                         session: Annotated[Session, Depends(get_session)],
                         user_data: Annotated[str | None, Depends(get_current_user)]):
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return order

    return {"OrderItem":order.items}

@app.patch("/order_update/{order_id}")
def update_order(order_id: int, 
                 order_in: UpdateOrder, 
                 session: Annotated[Session, Depends(get_session)],
                 user_data: Annotated[str | None, Depends(get_current_user)]):
     order_to_update = session.get(Order, order_id)
     if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
     if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
     return order

     order_data = order_in.model_dump(exclude_unset=True)
     order = order_to_update.sqlmodel_update(order_data)
     session.add(order)
     session.commit()
     session.refresh(order)
     return {"Updated Order":order}

@app.patch("/item_update/{order_id}")
def update_item(order_id: int,
                item_in: UpdateItem, 
                session: Annotated[Session, Depends(get_session)],
                user_data: Annotated[str | None, Depends(get_current_user)]):
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return order
    item_to_update = session.get(OrderItem,order_id)
    item_data = item_in.model_dump(exclude_unset=True)
    item = item_to_update.sqlmodel_update(item_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return {"Updated Item":item}
