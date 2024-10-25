from aiokafka import AIOKafkaProducer
from app.product_pb2 import Product  # Make sure product_pb2 is generated and available
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer

# Initialize Schema Registry client
schema_registry_client: SchemaRegistryClient = SchemaRegistryClient({"url": "http://localhost:8081"})

# Create Protobuf serializer
protobuf_serializer = ProtobufSerializer(msg_type=Product,
                                        schema_registry_client=schema_registry_client,
                                        conf={"use.deprecated.format": False}  # Set to False if backward compatibility is not needed
)

# Define the settings for Kafka
KAFKA_BROKER_URL = "broker:19092"
KAFKA_TOPIC = "products-topic"

async def produce_protobuf_message(producer: AIOKafkaProducer, topic: str, product: Product):
    """
    Produce a Protobuf message to Kafka.
    """
    # Serialize Protobuf message
    serialized_product = product.SerializeToString()
    print("Serialized Data:",serialized_product)
    # Send serialized data to Kafka
    await producer.send_and_wait(topic, serialized_product)
