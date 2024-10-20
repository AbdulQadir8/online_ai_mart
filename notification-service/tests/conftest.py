from collections.abc import Generator
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

import pytest
from sqlmodel import Session, delete

from app.core.db_engine import tests_engine as engine
from app.deps import get_session, get_kafka_producer 
from app.tests_pre_start import init_test_db
from app.main import app
from app.models.notification_model import Notification





@pytest.fixture(scope="module", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_test_db(session=session,db_engine=engine)
        yield session
        statement = delete(Notification)
        session.exec(statement=statement)

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
          # Override the get_current_admin_dep dependency
        
      
        async def mock_get_kafka_producer():
            yield mock_kafka_producer

        app.dependency_overrides[get_kafka_producer] = mock_get_kafka_producer

        with TestClient(app) as c:
            yield c
            # app.dependency_overrides.clear()

