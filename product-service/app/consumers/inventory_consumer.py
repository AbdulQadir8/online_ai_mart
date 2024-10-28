import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
from app.deps import get_session
from app.crud.product_crud import validate_product_by_id
from google.protobuf.json_format import MessageToDict
from app.proto import product_pb2

logging.basicConfig(level=logging.INFO)

async def consume_inventory_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="inventory-add-group",
        auto_offset_reset="earliest",
    )

    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    await consumer.start()

    try:
        async for message in consumer:
            logging.debug("\n\n RAW INVENTORY MESSAGE\n\n ")
            logging.debug(f"Received message on topic {message.topic}")
            logging.debug(f"Message Value {message.value}")

            # 1. Extract Product Id
            # inventory_data = json.loads(message.value.decode())
            # item = inventory_data["item"]
            # product_id = item["product_id"]
            # logging.debug("PRODUCT ID: %s", product_id)
            new_inventory = product_pb2.Inventory()
            new_inventory.ParseFromString(message.value)
            print(f"\n\n Iventory Deserialized Data: {new_inventory}")
            # Converts protobuf message to a dictionary.
            inventory_data = MessageToDict(new_inventory)
            product_id = inventory_data["product_id"]

            try:
                with next(get_session()) as session:
                    # 2. Check if Product Id is Valid
                    product = validate_product_by_id(product_id=product_id, session=session)
                    logging.debug("PRODUCT VALIDATION CHECK: %s", product)

                    if product is None:
                        # Handle invalid product case
                        logging.warning(f"Invalid product ID: {product_id}")
                        # Optionally send a message to another topic or take other action

                    if product is not None:
                        # Write new topic
                        logging.debug("PRODUCT VALIDATION CHECK NOT NONE")

                        await producer.send_and_wait(
                            "inventory-add-stock-response",
                            message.value
                        )

            except Exception as e:
                logging.error(f"Error validating product or sending message: {e}")

    except Exception as e:
        logging.error(f"Error consuming messages: {e}")

    finally:
        await consumer.stop()
        await producer.stop()
        logging.info("Consumer stopped.")
