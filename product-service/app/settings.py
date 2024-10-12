from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)


TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

EMAIL_TEST_USER = config("EMAIL_TEST_USER",cast=str)

AUTH_SERVER_URL = config("AUTH_SERVER_URL",cast=str)


FIRST_SUPERUSER = config("FIRST_SUPERUSER", cast=str)
FIRST_SUPERUSER_PASWORD = config("FIRST_SUPERUSER_PASSWORD",cast=str)