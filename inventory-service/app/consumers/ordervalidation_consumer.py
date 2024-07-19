
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.crud.inventory_crud import get_quantity_value, decrease_quantity_value
from app.deps import get_session, get_kafka_producer
# from app.hello_ai import chat_completion

async def consume_order_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="ordervalidation_consumer_group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW INVENTORY MESSAGE\n\n ")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract  Quantity value
            order_data = json.loads(message.value.decode())
            orderitem = order_data.get("orderitem")

            
            orderitem_json = json.dumps(orderitem).encode("utf-8")
            print("orderitem_JSON:", orderitem_json)

            product_id = orderitem_json["product_id"]
            quantity_value = orderitem_json["quantity"]
            print("Product ID", product_id)
            print("Quantity Value", quantity_value)

            # 2. Check if Product Id is Valid
            with next(get_session()) as session:
                real_quantity = get_quantity_value(
                    product_id=product_id, session=session)
                print("Quantity VALIDATION CHECK", real_quantity)
                # 3. If Valid
                if real_quantity < quantity_value:
                    pass
                    # email_body = chat_completion(f"Inventory is not available. Write Email to Admin {product_id}")
                    
                if real_quantity >= quantity_value:
                    with next(get_session()) as session:
                        updated_inventory = decrease_quantity_value(product_id=product_id, real_quantity=real_quantity,
                                                                   quantity_value=quantity_value, session=session)
                        print("Inventory Updated: ",updated_inventory)

                            # - Write New Topic
                        producer = AIOKafkaProducer(
                            bootstrap_servers='broker:19092')
                        await producer.start()
                        try:
                            await producer.send_and_wait(
                                "InventoryReserved",
                                message.value
                            )
                        finally:
                            await producer.stop()

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()