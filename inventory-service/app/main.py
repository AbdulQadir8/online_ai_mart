# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.inventory_model import InventoryItem, InventoryItemUpdate
from app.crud.inventory_crud import add_new_inventory_item, delete_inventory_item_by_id, get_all_inventory_items, get_inventory_item_by_id
from app.deps import get_session, get_kafka_producer
from app.consumers.add_stock_consumer import consume_messages
from app.consumers.ordervalidation_consumer import consume_order_messages

from fastapi.security import OAuth2PasswordRequestForm
from app import requests
from app.deps import GetCurrentAdminDep

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tabl...")
    create_db_and_tables()



    task1 = asyncio.create_task(consume_messages("inventory-add-stock-response", 'broker:19092'))
    task2 = asyncio.create_task(consume_order_messages("order_events", "broker:19092"))

        

    yield

 


app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Product Service"}


@app.post("/login-endpoint", tags=["Wrapper Auth"])
def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
     auth_token = requests.login_for_access_token(form_data)
     # Make a request to get user data and check if user is admin
     user = requests.get_current_user(auth_token.get("access_token"))
     if user.get("is_superuser") == False:
          raise HTTPException(status_code=403, detail="User doesn't have enough privileges")
     return auth_token


@app.post("/manage-inventory/", dependencies=[GetCurrentAdminDep],response_model=InventoryItem)
async def create_new_inventory_item(item: InventoryItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new inventory item and send it to Kafka"""

    item_dict = {field: getattr(item, field) for field in item.dict()}
    item_event = {"action":"create",
                  "item":item_dict}
    item_json = json.dumps(item_event).encode("utf-8")
    print("item_JSON:", item_json)
    # Produce message
    await producer.send_and_wait("AddStock", item_json)
    # new_item = add_new_inventory_item(item, session)
    return item


@app.get("/manage-inventory/all", response_model=list[InventoryItem], dependencies=[GetCurrentAdminDep])
def all_inventory_items(session: Annotated[Session, Depends(get_session)]):
    """ Get all inventory items from the database"""
    return get_all_inventory_items(session)


@app.get("/manage-inventory/{item_id}", response_model=InventoryItem, dependencies=[GetCurrentAdminDep])
def single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single inventory item by ID"""
    try:
        return get_inventory_item_by_id(inventory_item_id=item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/manage-inventory/{item_id}", response_model=dict, dependencies=[GetCurrentAdminDep])
async def delete_single_inventory_item(item_id: int, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
      """ Delete a single inventory item by ID"""
      item_event = {
          "action": "delete",
          "item_id": item_id
      }
      item_event_json = json.dumps(item_event).encode("utf-8")
      await producer.send_and_wait("inventory-add-stock-response", item_event_json)
      return {"status":"deleted"}


@app.patch("/manage-inventory/{item_id}",dependencies=[GetCurrentAdminDep])
async def update_single_inventoryitem(item_id: int, 
                                item: InventoryItemUpdate, 
                                producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
        item_dict = {field: getattr(item, field) for field in item.dict()}
        item_event = {
            "action": "update",
            "item_id": item_id,
            "item": item_dict
        }
        item_event_json = json.dumps(item_event).encode("utf-8")
        await producer.send_and_wait("inventory-add-stock-response", item_event_json)

        return item
