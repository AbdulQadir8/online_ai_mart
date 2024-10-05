from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app import settings 
from app.core.db_engine import tests_engine as engine
from app.deps import get_session, get_kafka_producer
from app.tests_pre_start import init_test_db
from app.main import app
from app.models.order_model import Order, OrderItem
from tests.utils.utils import get_superuser_token_headers
from tests.utils.user import authentication_token_from_email


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:

    with Session(engine) as session:
        init_test_db(session=session,db_engine=engine)
        yield session
        statement = delete(Order)
        session.exec(statement)
        statement = delete(OrderItem)
        session.exec(statement)
        session.commit()

@pytest.fixture(scope="module")
def mock_kafka_producer():
    # Return a mock Kafka producer
    return AsyncMock()

@pytest.fixture(scope="module")
def client(mock_kafka_producer) -> Generator[TestClient, None, None]:
    with Session(engine) as session:
        def get_session_override():
            yield session

        app.dependency_overrides[get_session] = get_session_override

        # Ensure FastAPI uses the mock Kafka producer dependency
        async def mock_get_kafka_producer():
            yield mock_kafka_producer

        app.dependency_overrides[get_kafka_producer] = mock_get_kafka_producer
        with TestClient(app) as c:
            yield c



# @pytest.fixture(scope="module")
# def client() -> Generator[TestClient, None, None]:    
#     with Session(engine) as session:
#         def get_session_override():
#             yield session

#         app.dependency_overrides[get_session] = get_session_override
#         with TestClient(app)  as c:
#             print("Setting up Test client")
#             yield c

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)

@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )