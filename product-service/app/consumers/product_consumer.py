from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id, delete_product_by_id, update_product_by_id
from app.deps import get_session
from sqlmodel import Session


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-product-consumer-group",
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")

            event = json.loads(message.value.decode())
            
            action = event.get("action")
            product_data = event.get("product")
            print("TYPE", (type(product_data)))
            print(f"Product Data {product_data}")
            product_id = event.get("product_id")

            try:
                with next(get_session()) as session:
                    if action == "create" and product_data:
                        new_product = Product(**product_data)
                        db_insert_product = add_new_product(new_product, session=session)
                        print("DB_INSERT_PRODUCT", db_insert_product)
                    elif action == "delete" and product_id:
                        delete_product_by_id(product_id=product_id, session=session)
                        print({"status": f"Product deleted with Id:{product_id}"})
                    elif action == "update" and product_id and product_data:
                        new_product = ProductUpdate(**product_data)
                        updated_product = update_product_by_id(product_id, new_product, session)
                        print({"status": f"Product updated with ID:{product_id}", "product": updated_product})


            except Exception as e:
                print(f"Error processing message: {e}")
                # Event EMIT In NEW TOPIC

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()