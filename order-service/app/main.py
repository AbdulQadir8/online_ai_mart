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
from app.models.order_model import CreateOrder, Order, OrderItem, UpdateOrder
# from app.consumers.order_consumer import consume_messages
from app.crud.order_crud import get_single_order, add_new_order


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
    return {"Hellow": "Order Service"}

@app.post("/order/")
async def create_order(order_data: CreateOrder, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
        # order_dict = {field: getattr(order, field) for field in order.dict()}
        # item_dict = {field: getattr(orderitem, field) for field in orderitem.dict()}


        # order_item_dict = {"order":order_dict,
        #                    "orderitem":item_dict}

        # order_json = json.dumps(order_item_dict).encode("utf-8")
        # print("orderJSON:", order_json)
        # # Produce message
        # await producer.send_and_wait("order_events", order_json)
        # # session.add(new_order)
        # # session.commit()
        # # session.refresh(new_order)
        # return order_item_dict

        # Convert the CreateOrderItem Pydantic model to the SQLAlchemy model
        db_order = Order(
            user_id=order_data.user_id,
            status=order_data.status,
            total_amount=order_data.total_amount
        )

        # Convert each CreateOrderItem to an OrderItem and add to db_order.items
        for item_data in order_data.items:
            db_item = OrderItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price
            )
            db_order.items.append(db_item)
        
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        return order_data


@app.get("/orders/", response_model=list[Order])
def read_orders(session: Annotated[Session, Depends(get_session)]):
        orders = session.exec(select(Order)).all()
        return orders


@app.get("/order/{order_id}")
def get_order_by_id(order_id:int, session: Annotated[Session, Depends(get_session)]):
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one()
    return order

@app.get("/orderitem/{order_id}")
def get_order_and_item_by_id(order_id:int, session: Annotated[Session, Depends(get_session)]):
    statement = select(Order).where(Order.id == order_id)
    result = session.exec(statement)
    order = result.one()
    return {"Order":order,
            "OrderItem":order.items}

@app.get("/orderitem/{order_id}")
def orderitem_by_orderid(order_id:int, session: Annotated[Session, Depends(get_session)]):
    statement = select(OrderItem).where(OrderItem.order_id == order_id)
    result = session.exec(statement)
    orderitem = result.one()
    return orderitem

@app.patch("/order_update/{order_id}")
def update_order(order_id: int, order_in: UpdateOrder, session: Session):
     order_to_update = session.get(Order, order_id).one_or_none()
     order_data = order_in.model_dump(exclude_unset=True)
     order = order_to_update.sqlmodel_update(order_data)
     session.add(order)
     session.commit()
     session.refresh(order)
     return order

