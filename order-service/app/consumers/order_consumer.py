from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.models.order_model import Order, OrderItem, OrderItem
from app.deps import get_session
import logging
logging.basicConfig(level=logging.INFO)
import json


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="order_consumer-group",
        auto_offset_reset='earliest'
    )
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    
    await producer.start()
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            try:
                logging.info("RAW ORDER MESSAGE")
                logging.info(f"Received message on topic {message.topic} at offset {message.offset}")
                logging.info(f"Message Value: {message.value}")
                # Here you can add code to process each message.
                # Example: parse the message, store it in a database, etc.
                order_data = json.loads(message.value.decode())
                logging.info(f"Decoded order_data:{order_data}")
                with next(get_session()) as session:
                    # Convert the CreateOrderItem Pydantic model to the SQLAlchemy model
                    db_order = Order(
                        user_id=order_data["user_id"],
                        status=order_data["status"],
                        total_amount=order_data["total_amount"]
                    )
                    # Convert each CreateOrderItem to an OrderItem and add to db_order.items
                    for item_data in order_data["items"]:
                        db_item = OrderItem(
                            product_id=item_data["product_id"],
                            quantity=item_data["quantity"],
                            price=item_data["price"]
                        )
                        db_order.items.append(db_item)
                    
                    session.add(db_order)
                    session.commit()
                    session.refresh(db_order)
                    logging.info(f"DB ORDER:{db_order}")
                    order_dict = {"id":db_order.id,"user_id":db_order.user_id,"total_amount":db_order.total_amount}
                    order_json = json.dumps(order_dict).encode("utf-8")
                    await producer.send_and_wait("order_payment_events",order_json)
                # Commit the message offset after successful processing
                await consumer.commit()
            except Exception as e:
                logging.info({"error":e})
                
    finally:
        await producer.stop()
        logging.info("Produer Stopped")
        await consumer.stop()
        logging.info("Cosnumer Stopped")
