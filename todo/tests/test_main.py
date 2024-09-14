from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app import settings
from app.main import app, get_session
import pytest

#================================================================================================================================
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
#============================================================================================================
#Refactor with fixture pytest
# 1-Arrange 2-Act 3-Assert 4- Cleanup
@pytest.fixture(scope="module",autouse=True)
def get_db_session():
    SQLModel.metadata.create_all(engine)
    yield Session(engine)

@pytest.fixture(scope='function')
def test_app(get_db_session):
    def test_session():
        yield get_db_session
    app.dependency_overrides[get_session] = test_session
    with TestClient(app=app) as client:
        yield client
        



#============================================================================================================

# Test-1: read_root test
def test_read_root(test_app):
    # client = TestClient(app=app)
    response = test_app.get("/")
    data =response.json()
    assert response.status_code == 200
    assert data == {"Hello": "Todo App"}

# Test-2 post test
def test_create_todo(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def db_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = db_session_override
    #     client = TestClient(app=app)
    test_todo = {"content":"create todo", "is_completed":False}
    response = test_app.post('/todos/',json=test_todo)
    data = response.json()
    assert response.status_code == 200
    assert data["content"] == test_todo["content"]

# Test-3 get all todo test
def test_read_todos(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def db_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = db_session_override
    #     client = TestClient(app=app)
    test_todo = {"content":"get all todo", "is_completed":False}
    test_app.post("/todos", json=test_todo)
    response = test_app.get("/todos/")
    data = response.json()[-1]
    assert response.status_code == 200
    assert data["content"] == test_todo["content"]

# Test-4 Get single todo
def test_read_single_todo(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def db_session_override():
    #         return session
    # app.dependency_overrides[get_session] = db_session_override
    # client = TestClient(app=app)
    test_todo = {"content":"Get single todo", "is_completed":False}
    response = test_app.post("/todos/", json=test_todo)
    todo_id = response.json()["id"]

    response = test_app.get(f"/todos/{todo_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["content"] == test_todo["content"]

# Test-5 edit todo
def test_update_todo(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def db_session_override():
    #         return session
    # app.dependency_overrides[get_session] = db_session_override
    # client = TestClient(app=app)
    test_todo = {"content":"edit single todo", "is_completed":False}
    response = test_app.post("/todos/", json=test_todo)
    todo_id = response.json()["id"]

    edited_todo = {"content":"edit todo", "is_completed":False}
    response = test_app.put(f"/todos/{todo_id}",json=edited_todo)
    data = response.json()

    assert response.status_code == 200
    assert data["content"] == edited_todo["content"]

# Test-6 Delete todo
def test_delete_todo(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def db_session_override():
    #         return session
    # app.dependency_overrides[get_session] = db_session_override
    # client = TestClient(app=app)
    test_todo = {"content":"Todo to delete","is_completed":False}
    response = test_app.post("/todos/",json=test_todo)
    todo_id = response.json()["id"]
    response = test_app.delete(f"/todos/{todo_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Todo deleted successfully"

