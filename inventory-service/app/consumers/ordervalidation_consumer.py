from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import logging
import json
import asyncio
from app.crud.inventory_crud import get_quantity_value, decrease_quantity_value
from app.deps import get_session, get_kafka_producer

logging.basicConfig(level=logging.INFO)


async def consume_order_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="ordervalidation_consumer_group",
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    
    await producer.start()
    await consumer.start()

    try:
        logging.info(f"Subscribed to topic: {topic}")

        async for message in consumer:
            try:
                logging.info("RAW INVENTORY MESSAGE")
                logging.info(f"Received message on topic {message.topic} at offset {message.offset}")
                logging.info(f"Message Value: {message.value}")

                # Extract Quantity value
                order_data = json.loads(message.value.decode())
                logging.info(f"Decoded order data: {order_data}")
                orderitem = order_data["orderitem"]

                product_id = orderitem["product_id"]
                quantity_value = orderitem["quantity"]
                logging.info(f"Product ID:, {product_id}")
                logging.info(f"Quantity Value:, {quantity_value}")

                # Check if Product Id is Valid
                with next(get_session()) as session:
                    real_quantity = get_quantity_value(product_id=product_id, session=session)
                    logging.info(f"Quantity VALIDATION CHECK:, {real_quantity}")

                    # If Valid
                    if real_quantity >= quantity_value:
                        updated_inventory = decrease_quantity_value(
                            product_id=product_id,
                            quantity_value=quantity_value,
                            session=session
                        )
                        logging.info(f"Inventory Updated:, {updated_inventory}")

                        # Write New Topic
                        await producer.send_and_wait(
                            "InventoryReserved",
                            message.value
                        )
                    else:
                        logging.info(f"Not enough inventory for product ID, {product_id}")
                        # Handle the case where there is not enough inventory
                        # For example, notify someone or write to another topic

                # Commit the message offset after successful processing
                await consumer.commit()
            
            except Exception as e:
                logging.info(f"Error processing message: {e}")
                # Optionally, handle the exception (e.g., write to a dead-letter queue)

    finally:
        await producer.stop()
        logging.info("Produer Stopped")
        await consumer.stop()
        logging.info("Cosnumer Stopped")

        


