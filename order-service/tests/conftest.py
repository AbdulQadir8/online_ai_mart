from collections.abc import Generator
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session, delete

from app import settings 
from app.core.db_engine import tests_engine as engine
from app.core.requests import get_current_user, login_for_access_token
from app.deps import get_session, get_kafka_producer
from app.tests_pre_start import init_test_db
from app.main import app
from app.models.order_model import Order, OrderItem
from tests.utils.utils import get_superuser_token_headers
from tests.utils.user import authentication_token_from_email


  # Mocked user data returned from `get_current_user`
mock_user_data = {
                 "user_name": "usama123",
                 "email": "usama123",
                 "is_active": True,
                 "is_superuser": True,
                 "full_name": "Usama Ali",
                 "role": "admin",
                 "id": 1
                 }
# Mock order data for testing

# Sample order data for the test (including items list)
order_data = {
    "id":2,
    "status": "pending",
    "total_amount": 200.00,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "items": [
        {
            "product_id": 1,
            "quantity": 2,
            "price": 50.00
        },
        {
            "product_id": 2,
            "quantity": 1,
            "price": 100.00
        }
    ]
}



# Test cases for the get_order_by_id route



@pytest.fixture(scope="module", autouse=True)
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
        def mock_kafka_producer():
          # Return a mock Kafka producer
          return AsyncMock()

        async def mock_get_kafka_producer():
            yield mock_kafka_producer

        app.dependency_overrides[get_kafka_producer] = mock_get_kafka_producer

        def login_for_access_token_override():
            pass
        app.dependency_overrides[login_for_access_token] = login_for_access_token_override   
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