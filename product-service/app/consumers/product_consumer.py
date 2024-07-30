import logging
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import add_new_product, get_product_by_id, delete_product_by_id, update_product_by_id
from app.deps import get_session

# Set the logging level to INFO for aiokafka to reduce verbosity
logging.basicConfig(level=logging.INFO)

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-product-consumer-group",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    try:
        async for message in consumer:
            logging.info(f"Received message on topic {message.topic}")

            try:
                event = json.loads(message.value.decode())
                action = event.get("action")
                product_data = event.get("product")
                product_id = event.get("product_id")

                logging.info(f"Action: {action}")
                logging.info(f"Product Data: {product_data}")
                logging.info(f"Product ID: {product_id}")

                with next(get_session()) as session:
                    if action == "create" and product_data:
                        new_product = Product(**product_data)
                        db_insert_product = add_new_product(new_product, session=session)
                        logging.info(f"Product created: {db_insert_product}")
                    elif action == "delete" and product_id:
                        delete_product_by_id(product_id=product_id, session=session)
                        logging.info(f"Product deleted with ID: {product_id}")
                    elif action == "update" and product_id and product_data:
                        new_product = ProductUpdate(**product_data)
                        updated_product = update_product_by_id(product_id, new_product, session)
                        logging.info(f"Product updated with ID: {product_id}, Product: {updated_product}")

            except Exception as e:
                logging.error(f"Error processing message: {e}")
                # Optionally handle the error, such as by sending to a different topic

    finally:
        await consumer.stop()
        logging.info("Consumer stopped.")
