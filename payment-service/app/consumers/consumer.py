from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
from app.models.payment_model import Payment, Transaction
from app.deps import get_session
from app import settings
import logging
logging.basicConfig(level=logging.INFO)

async def consume_order_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=settings.KAFKA_CONSUMER_INVENTORY_RESERVED_GROUP_ID,
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await consumer.start()

    try:
        async for message in consumer:
            logging.info("RAW INVENTORY MESSAGE")
            # logging.info(f"Received message on topic {message.topic} at offset {message.offset}")
            logging.info(f"Message Value: {message.value}")

            order_data = json.loads(message.value.decode())
            logging.info(f"Decoded order data: {order_data}")

            order_id = order_data["id"]
            user_id = order_data["user_id"]
            amount = order_data["total_amount"]
            # Step 1: Create Payment Record
            with next(get_session()) as session:
                payment = Payment(order_id=order_id, user_id=user_id, amount=amount, currency="usd", status="pending")
                session.add(payment)
                session.commit()
            
                # Step 2: Initiate Transaction
                transaction = Transaction(payment_id=payment.id, status="initiated",amount=amount)
                session.add(transaction)
                session.commit()
            

    except Exception as e:
        logging.info(f"Error processing message: {e}")
        # Optionally, handle the exception (e.g., write to a dead-letter queue)           
    finally:
        await consumer.stop()
