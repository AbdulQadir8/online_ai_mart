import logging
from aiokafka import AIOKafkaConsumer
from app.deps import get_session
from app.crud.inventory_crud import add_new_inventory_item, delete_inventory_item_by_id, update_item_by_id
from app.models.inventory_model import InventoryItem, InventoryItemUpdate

from google.protobuf.json_format import MessageToDict
from app.proto import inventory_pb2


logging.basicConfig(level=logging.INFO)

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="add-stock-consumer-group",
        auto_offset_reset="earliest",
    )

    await consumer.start()
    logging.info("Consumer started and subscribed to topic.")
    try:        
        async for message in consumer:
            # logging.info(f"Received message: {message}")
            # event = json.loads(message.value.decode())
            # action = event.get("action")
            # item_data = event.get("item")
            # item_id = event.get("item_id")
            new_inventory = inventory_pb2.Inventory()
            new_inventory.ParseFromString(message.value)
            print(f"\n\n Iventory Deserialized Data: {new_inventory}")
            # Converts protobuf message to a dictionary.
            item_data = MessageToDict(new_inventory,preserving_proto_field_name=True)
            action = item_data["action"]
            item_id = item_data.get("item_id")
            


            logging.info(f"Action: {action}, Item Data: {item_data}, Item ID: {item_id}")

            try:
                with next(get_session()) as session:
                    if action == "create" and item_data:
                        db_insert_product =  add_new_inventory_item(
                            inventory_item_data=InventoryItem(**item_data),
                            session=session
                        )
                    elif action == "delete" and item_id:
                        delete_inventory_item_by_id(
                            inventory_item_id=item_id,
                            session=session
                        )
                    elif action == "update" and item_id:
                        update_item_by_id(
                            item_id=item_id,
                            to_update_item_data=InventoryItemUpdate(**item_data),
                            session=session
                        )
            except Exception as e:
                print(f"Error processing message: {e}")
                # Event EMIT In NEW TOPIC

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc

    except Exception as e:
        logging.error(f"Error consuming messages: {e}")
    finally:
        await consumer.stop()
        logging.info("Consumer stopped.")

# Run the consumer
# You can call consume_messages(topic, bootstrap_servers) within your async event loop
