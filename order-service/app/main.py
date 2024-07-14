# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app import settings
from app.models.order_model import Order, OrderItem
import asyncio
import json
from app.db_engine import engine
from app.deps import get_kafka_producer, get_session
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
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(consume_messages(settings.KAFKA_ORDER_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Order": "Service"}


@app.post("/todos/", response_model=Order)
async def create_order(order: Order, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)])->Order:
        order_dict = {field: getattr(order, field) for field in order.dict()}
        order_json = json.dumps(order_dict).encode("utf-8")
        print("todoJSON:", order_json)
        # Produce message
        await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, order_json)
        # session.add(todo)
        # session.commit()
        # session.refresh(todo)
        return 


@app.get("/orders/", response_model=list[Order])
def read_orders(session: Annotated[Session, Depends(get_session)]):
        orders = session.exec(select(Order)).all()
        return orders
