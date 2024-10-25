# import logging
# from aiokafka import AIOKafkaConsumer
# from app.models.product_model import UpdateProduct, CreateProduct
# from app.crud.product_crud import add_new_product, delete_product_by_id, update_product_by_id
# from app.deps import get_session
# from google.protobuf.json_format import MessageToDict
# from app import product_pb2

# # Set the logging level to INFO for aiokafka to reduce verbosity
# logging.basicConfig(level=logging.INFO)

# async def consume_messages(topic, bootstrap_servers):
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=bootstrap_servers,
#         group_id="my-product-consumer-group",
#         auto_offset_reset="earliest",
#     )

#     await consumer.start()
#     try:
#         async for message in consumer:
#             logging.info(f"Received message on topic {message.topic}")

#             try:
#                 # event = json.loads(message.value.decode())
                
#                 new_product = product_pb2.Product()
#                 new_product.ParseFromString(message.value)
#                 print(f"\n\n Consumer Deserialized data: {new_product}")
#                 # Converts protobuf message to a dictionary.
#                 product_data = MessageToDict(new_product)
#                 action = product_data.get("action")
#                 product_id = product_data.get("productId")

#                 logging.info(f"Action: {action}")
#                 logging.info(f"Product Data: {product_data}")
#                 logging.info(f"Product ID: {product_id}")

#                 with next(get_session()) as session:
#                     if action == "create" and product_data:
#                         product_in = CreateProduct(**product_data)
#                         db_insert_product = add_new_product(product_data=product_in, session=session)
#                         logging.info(f"Product created: {db_insert_product}")
#                     elif action == "delete" and product_id:
#                         delete_product_by_id(product_id=product_id, session=session)
#                         logging.info(f"Product deleted with ID: {product_id}")
#                     elif action == "update" and product_id and product_data:
#                         new_product = UpdateProduct(**product_data)
#                         updated_product = update_product_by_id(product_id, new_product, session)
#                         logging.info(f"Product updated with ID: {product_id}, Product: {updated_product}")

#             except Exception as e:
#                 logging.error(f"Error processing message: {e}")
#                 # Optionally handle the error, such as by sending to a different topic

#     finally:
#         await consumer.stop()
#         logging.info("Consumer stopped.")




import logging
from aiokafka import AIOKafkaConsumer
from app.models.product_model import UpdateProduct, CreateProduct
from app.crud.product_crud import add_new_product, delete_product_by_id, update_product_by_id
from app.deps import get_session
from google.protobuf.json_format import MessageToDict
from app import product_pb2

# Import Schema Registry and Protobuf deserializer
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient

logging.basicConfig(level=logging.INFO)

async def consume_messages(topic: str, bootstrap_servers: str, schema_registry_url: str):
    # Schema Registry client setup
    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
    
    # Protobuf deserializer for Product schema
    protobuf_deserializer = ProtobufDeserializer(product_pb2.Product,
                                                conf={"use.deprecated.format": False}  # Set to True if backward compatibility is needed
                                                )
    # Consumer configuration with deserializer
    consumer_conf = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": "my-product-consumer-group",
        "auto.offset.reset": "earliest",
        "value.deserializer": protobuf_deserializer,
    }
    
    consumer = DeserializingConsumer(consumer_conf)
    consumer.subscribe([topic])

    try:
        while True:
            message = consumer.poll(1)
            if message is None:
                continue
            if message.error():
                logging.error(f"Consumer error: {message.error()}")
                continue

            product_data = MessageToDict(message.value())
            action = product_data.get("action")
            product_id = product_data.get("productId")

            logging.info(f"Action: {action}")
            logging.info(f"Product Data: {product_data}")
            logging.info(f"Product ID: {product_id}")

            with next(get_session()) as session:
                if action == "create" and product_data:
                    product_in = CreateProduct(**product_data)
                    db_insert_product = add_new_product(product_data=product_in, session=session)
                    logging.info(f"Product created: {db_insert_product}")
                elif action == "delete" and product_id:
                    delete_product_by_id(product_id=product_id, session=session)
                    logging.info(f"Product deleted with ID: {product_id}")
                elif action == "update" and product_id and product_data:
                    new_product = UpdateProduct(**product_data)
                    updated_product = update_product_by_id(product_id, new_product, session)
                    logging.info(f"Product updated with ID: {product_id}, Product: {updated_product}")

    finally:
        consumer.close()
        logging.info("Consumer stopped.")
