from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
from app.deps import process_notification
import logging
logging.basicConfig(level=logging.INFO)

import json

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification_consumer_group_id",
        auto_offset_reset='earliest'
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message: {message.value.decode()} on topic {message.topic}")
            event_data = json.loads(message.value.decode())
            await process_notification(event_data)  # Process and send notification
            logging.info("Notification Process Completed")
            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


