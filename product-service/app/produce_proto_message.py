from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from aiokafka import AIOKafkaProducer
from app import settings

schema_str: str= """
syntax = "proto3";

package product;

message Product {
    string name = 1;            
    string description = 2;    
    double price = 3;           
    string expiry = 4;           
    string brand = 5;          
    string weight = 6;          
    string category = 7;         
    string sku = 8;
    int32 product_id = 9;              
    string action = 10;           
}


"""


class SerializationContext:
    def __init__(self, topic: str, field: str = "value"):
        self.topic = topic
        self.field = field  # Provide a default non-None field value

async def produce_protobuf_message(producer: AIOKafkaProducer, topic: str, product):
    schema_registry_conf = {
        'url': settings.SCHEMA_REGISTRY_URL,
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    schema = Schema(schema_str=schema_str,
                    schema_type="PROTOBUF")

    schema_id = schema_registry_client.register_schema(subject_name="new-schema-value",
                                           schema=schema)
    print(f"Schema Registered with Id:{schema_id}")
    
    serializer = ProtobufSerializer(
        product.__class__, 
        schema_registry_client, 
        {'use.deprecated.format': False}
    )
    
    # Use the topic and a default 'field' name
    context = SerializationContext(topic, field="value")
    
    serialized_product = serializer(product, context)
    
    await producer.send_and_wait(topic, serialized_product)
