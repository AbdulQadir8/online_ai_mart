# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence

from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
from app.db_engine import engine
import asyncio
import json
from app.deps import get_kafka_producer, get_session
from app.models.order_model import Order, OrderItem
from app.consumers.order_consumer import consume_messages


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
    # task = asyncio.create_task(consume_messages('order_events', 'broker:19092'))
    yield



app = FastAPI(
     lifespan=lifespan, 
     title="Hello World API with DB", 
     version="0.0.1")


@app.get("/")
def read_root():
    return {"Hello1": "Order Service"}

@app.post("/order/")
async def create_order(order: Order, orderitem: OrderItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
        order_dict = {field: getattr(order, field) for field in order.dict()}
        item_dict = {field: getattr(orderitem, field) for field in orderitem.dict()}


        order_item_dict = {"order":order_dict,
                           "orderitem":item_dict}

        order_json = json.dumps(order_item_dict).encode("utf-8")
        print("orderJSON:", order_json)
        # Produce message
        await producer.send_and_wait("order_events", order_json)
        # session.add(new_order)
        # session.commit()
        # session.refresh(new_order)
        return order_item_dict


@app.get("/orders/", response_model=list[Order])
def read_orders(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Order)).all()
        return todos
