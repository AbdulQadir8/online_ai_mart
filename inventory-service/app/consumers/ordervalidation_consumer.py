from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import logging
import json
from app.crud.inventory_crud import get_quantity_value, decrease_quantity_value
from app.deps import get_session
from google.protobuf.json_format import MessageToDict
import ast

from app.proto import order_pb2

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

                # Log the length of the message for debugging
                logging.info(f"Length of received message: {len(message.value)} bytes")

                # Attempt to deserialize the Protobuf message
                protobuf_message = order_pb2.OrderMessage()
                
                # Log before parsing
                logging.info("Attempting to deserialize message...")
                
                protobuf_message.ParseFromString(message.value)

                # Accessing data from the deserialized attributes
                logging.info(f"Deserialized Data:, {protobuf_message}")
            
                item = ast.literal_eval(protobuf_message.items)
                logging.info(f"Item: {item}")
                product_id = item["product_id"]
                quantity_value = item["quantity"]
                price = item["price"]

   

             
                logging.info(f"Product ID:, {product_id}")
                logging.info(f"Quantity Value:, {quantity_value}")
                logging.info(f"Price: {price}")

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

        


