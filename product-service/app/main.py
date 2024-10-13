# main.py
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app import requests
from typing import Annotated, AsyncGenerator
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
import asyncio
import json
from aiokafka import AIOKafkaProducer

from app import settings
from app.core.db_engine import engine
from app.models.product_model import Product, UpdateProduct, CreateProduct, PublicProduct
from app.crud.product_crud import get_all_products, get_product_by_id, delete_product_by_id, validate_product_by_id
from app.deps import get_session, get_kafka_producer, get_current_admin_dep
from app.consumers.product_consumer import consume_messages
from app.consumers.inventory_consumer import consume_inventory_messages
# from app.hello_ai import chat_completion


ALGORITHM: str = "HS256"
SECRET_KEY: str = "The new Secret key"


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting application lifespan...")
    create_db_and_tables()

    task1 = asyncio.create_task(consume_messages(settings.KAFKA_PRODUCT_TOPIC, 'broker:19092'))
    task2 = asyncio.create_task(consume_inventory_messages("AddStock", 'broker:19092'))

    yield



app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
    # servers=[
    #     {
    #         "url": "http://product-service:8005", # ADD NGROK URL Here Before Creating GPT Action
    #         "description": "Development Server"
    #     }
    #     ]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-endpoint")


@app.get("/")
def read_root():
    return {"Hello1": "Product Service"}

@app.post("/login-endpoint", tags=["Wrapper Auth"])
def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    auth_token = requests.login_for_access_token(form_data)
    # Make a request to get user data and check if user is admin
    user = requests.get_current_user(auth_token.get("access_token"))
    if user.get("is_superuser") == False:
        raise HTTPException(status_code=403, detail="User doesn't have enough privileges")
    return auth_token
@app.post("/manage-products/")
async def create_new_product(
    token: Annotated[str | None, Depends(get_current_admin_dep)],
    product: CreateProduct, 
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """ Create a new product and send it to Kafka"""
    # try:
    #     decoded_token_data = jwt.decode(token, SECRET_KEY , algorithms=[ALGORITHM])
    # except JWTError as e:
    #     return {"errorz": str(e)}
    product_dict = {field: getattr(product, field) for field in product.model_dump()}
    product_dict["expiry"] = product.expiry.isoformat()
    product_event = {
        "action": "create",
        "product": product_dict
    }
    product_json = json.dumps(product_event).encode("utf-8")
    print("product_JSON:", product_event)
    
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json)
    return product
            

@app.get("/manage-products/all")
def call_all_products(token: Annotated[str | None, Depends(get_current_admin_dep)],session: Annotated[Session, Depends(get_session)]):
    """ Get all products from the database"""

    return get_all_products(session)

@app.get("/manage-products/{product_id}",response_model=PublicProduct)
def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)],
                       token: Annotated[str | None, Depends(get_current_admin_dep)]):
    """ Get a single product by ID"""
    product = get_product_by_id(product_id=product_id, session=session)
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")
    return product

@app.delete("/manage-products/{product_id}", response_model=dict)
async def delete_single_product(
    product_id: int, 
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[str | None, Depends(get_current_admin_dep)]
):
    """ Delete a single product by ID"""
    product = validate_product_by_id(product_id=product_id,session=session)
    if not product:
        raise HTTPException(status_code=400, detail=f"Product not found with this {product_id}")
    product_event = {
        "action": "delete",
        "product_id": product_id
    }
    product_event_json = json.dumps(product_event).encode("utf-8")
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_event_json)

    delete_product_by_id(product_id, session)
    return {"status": "Product deleted successfully"}

@app.patch("/manage-products/{product_id}",response_model=dict)
async def update_single_product(
    product_id: int, 
    product: UpdateProduct,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    token: Annotated[str | None, Depends(get_current_admin_dep)]
):
    """Update Product by id"""
    product = validate_product_by_id(product_id=product_id,session=session)
    if not product:
       raise HTTPException(status_code=400, detail=f"Product not found with this {product_id}")
    product_dict = {field: getattr(product, field) for field in product.model_dump()}
    product_event = {
        "action": "update",
        "product_id": product_id,
        "product": product_dict
    }
    product_event_json = json.dumps(product_event).encode("utf-8")
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_event_json)

    return {"message":"Product Updated Successfully"}
# @app.get("/hello-ai")
# def get_ai_response(prompt:str):
#     return chat_completion(prompt)
