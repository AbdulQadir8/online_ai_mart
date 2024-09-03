# from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
# import logging
# logging.basicConfig(level=logging.INFO)
# import json


# async def consume_messages(topic, bootstrap_servers):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=bootstrap_servers,
#         group_id="order_consumer-group",
#         auto_offset_reset='earliest'
#     )

#     # Start the consumer.
#     await consumer.start()
#     try:
#         # Continuously listen for messages.
#         async for message in consumer:
#             try:
#                 logging.info("RAW INVENTORY MESSAGE")
#                 logging.info(f"Received message on topic {message.topic} at offset {message.offset}")
#                 logging.info(f"Message Value: {message.value}")
#                 # Here you can add code to process each message.
#                 # Example: parse the message, store it in a database, etc.
#                 order_data = json.loads(message.value.decode())
#                 logging.info(f"Decoded order_data:{order_data}")

                
#     finally:
#         # Ensure to close the consumer when done.
#         await consumer.stop()