# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel
from typing import AsyncGenerator, Annotated
from aiokafka import AIOKafkaProducer
import asyncio
from app.db_engine import engine
from app.consumers.consumer import consume_messages
from app.deps import get_session, get_kafka_producer
import json



def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    
    task = asyncio.create_task(consume_messages('notification_events', 'broker:19092'))
    yield


app = FastAPI(lifespan=lifespan, title="Notification Service api with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8010", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        },{
            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])


@app.get("/")
def read_root():
    return {"App": "Notification Service"}
@app.post("/notifications/")
async def create_notification(user_id: int, message: str,
                              producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    notification_data = {
        "user_id": user_id,
        "message": message,
        "notification_type": "email"
    }
    notification_json = json.dumps(notification_data).encode("utf-8")
    # Publish to Kafka topic for processing
    await producer.send_and_wait("notification_events", notification_json)
    return {"status": "Notification enqueued"}

@app.get("/notifications/{notification_id}")
async def get_notification_status(notification_id: int):
    notification = session.get(Notification, notification_id)
    if not notification:
        return {"error": "Notification not found"}
    return {
        "user_id": notification.user_id,
        "message": notification.message,
        "status": notification.status,
        "created_at": notification.created_at,
        "updated_at": notification.updated_at
    }
