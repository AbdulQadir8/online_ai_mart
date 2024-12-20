# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Field, Session, SQLModel,select

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
from app.core.db_engine import engine
import asyncio
from app.deps import get_kafka_producer, get_session
from app.models.order_model import CreateOrder, Order, OrderItem, UpdateOrder, UpdateItem, OrderItem
from app.consumers.order_consumer import consume_messages
from app.core.requests import get_current_user, login_for_access_token
from app.proto import order_pb2

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
    return {"Hellow1": "Order Service"}

@app.post("/login-endpoint", tags=["Wrapper Auth"])
def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
    auth_token = login_for_access_token(form_data)
    return auth_token

@app.post("/order/")
async def create_order(order_data: CreateOrder,
                       producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
                       user_data: Annotated[str | None, Depends(get_current_user)]):
    """ Create a new inventory item and send it to Kafka"""
      

    pb_order_data = order_pb2.OrderMessage(
        user_id=user_data["id"],
        user_email=user_data["email"],
        status=order_data.status,  
        total_amount=order_data.total_amount,
        created_at=order_data.created_at.isoformat(),
        updated_at=order_data.updated_at.isoformat(),
        items= str({
            "product_id":order_data.items[0].product_id,
            "quantity":order_data.items[0].quantity,
            "price":order_data.items[0].price})
    )

    print(f"Order Protobuf Data: {pb_order_data}")
    serialized_data = pb_order_data.SerializeToString()
    print("Order Serialized_data: ",serialized_data)

    # Deserialize the UserProfile message
    deserialized_order_data = order_pb2.OrderMessage()
    deserialized_order_data.ParseFromString(serialized_data)

    # Accessing data from the deserialized attributes
    print("Deserialized Data:", deserialized_order_data)
    # for item in deserialized_order_data.items:
    #     print(f"product_id: {item.product_id}")
    #     print(f"Quantity: {item.quantity}")
    #     print(f"Price {item.price}")

    #Produce Message
    await producer.send_and_wait("order_events",serialized_data)
    return order_data

 

@app.get("/orders/", response_model=list[Order])
def read_orders(session: Annotated[Session, Depends(get_session)],
                user_data: Annotated[str | None, Depends(get_current_user)]):
        orders = session.exec(select(Order)).all()
        return orders


@app.get("/order/{order_id}")
def get_order_by_id(order_id:int, 
                    session: Annotated[Session, Depends(get_session)],
                    user_data: Annotated[str | None, Depends(get_current_user)]):
    order = get_order_by_id(order_id=order_id,session=session)
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return order

@app.get("/orderitem/{order_id}")
def get_order_and_item_by_id(order_id:int, 
                             session: Annotated[Session, Depends(get_session)],
                             user_data: Annotated[str | None, Depends(get_current_user)]):
    order = get_order_by_id(order_id=order_id,session=session)
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return {"Order":order,
            "OrderItem":order.items}

@app.get("/orderitem/{order_id}")
def orderitem_by_orderid(order_id:int, 
                         session: Annotated[Session, Depends(get_session)],
                         user_data: Annotated[str | None, Depends(get_current_user)]):
    order = get_order_by_id(order_id=order_id,session=session)
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    return {"OrderItem":order.items}

@app.patch("/order_update/{order_id}")
def update_order(order_id: int, 
                 order_in: UpdateOrder, 
                 session: Annotated[Session, Depends(get_session)],
                 user_data: Annotated[str | None, Depends(get_current_user)]):
    order_to_update = get_order_by_id(order_id=order_id,session=session)
    if order_to_update is None:
       raise HTTPException(status_code=404, detail="User Not Found")
    if order_to_update.user_id != user_data["id"]:
       raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")

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
    order = get_order_by_id(order_id=order_id,session=session)
    if order is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if order.user_id != user_data["id"]:
        raise HTTPException(status_code=403,detail="User doesn't  have enough privileges")
    item_to_update = session.get(OrderItem,order_id)
    item_data = item_in.model_dump(exclude_unset=True)
    item = item_to_update.sqlmodel_update(item_data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return {"Updated Item":item}
