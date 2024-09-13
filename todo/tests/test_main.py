from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app import settings
from app.main import app, get_session

# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency

# https://fastapi.tiangolo.com/tutorial/testing/
# https://realpython.com/python-assert-statement/
# https://understandingdata.com/posts/list-of-python-assert-statements-for-unit-tests/

# postgresql://ziaukhan:oSUqbdELz91i@ep-polished-waterfall-a50jz332.us-east-2.aws.neon.tech/neondb?sslmode=require
conn_string: str = str(settings.TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")

engine = create_engine(conn_string,
                        connect_args={},
                        pool_recycle=300
                        )

# Test-1: read_root test
def test_read_root():
    client = TestClient(app=app)
    response = client.get("/")
    data =response.json()
    assert response.status_code == 200
    assert data == {"Hello": "Todo App"}

# Test-2 post test
def test_create_todo():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def db_session_override():
            return session
        app.dependency_overrides[get_session] = db_session_override
        client = TestClient(app=app)
        test_todo = {"content":"create todo", "is_completed":False}
        response = client.post('/todos/',json=test_todo)
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == test_todo["content"]

