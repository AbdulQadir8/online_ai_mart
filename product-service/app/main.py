# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings 
from app.db_engine import engine
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id, delete_product_by_id, update_product_by_id
from app.deps import get_session, get_kafka_producer
from app.consumers.product_consumer import consume_messages


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
    task = asyncio.create_task(consume_messages(settings.KAFKA_PRODUCT_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8005", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

@app.get("/")
def read_root():
     return {"Hello":"Product Service"}

@app.post("/manage-products/", response_model=Product)
async def create_new_product(product: Product, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """Create a new product and send it to kafka"""

    product_dict = {field: getattr(product, field) for field in product.dict()}
    product_json = json.dumps(product_dict).encode("utf-8")
    print("product_JSON:",product_json)
    # Produce message
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json)
    # with next(session) as Session:
    #      new_product = add_new_product(product, session)
    return product


@app.get("/manage-products/all", response_model=list[Product])
def call_all_products(session: Annotated[Session, Depends(get_session)]):
     """Get all prducts from the database"""
     return get_all_products(session)

@app.get("/manage-products/{product_id}", response_model=list[Product])
def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a single product by ID"""
    try:
        return get_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.delete("/manage-products/{product_id}", response_model=dict)
def delete_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    """Delete a single product by ID"""
    try: 
        return delete_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/manage-products/{product_id}", response_model=Product)
def update_single_product(product_id: int, product: ProductUpdate, session: Annotated[Session, Depends(get_session)]):
    """Update a single product by ID"""
    try: 
        return update_product_by_id(product_id=product_id, to_update_product_data=product, session=session)
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))