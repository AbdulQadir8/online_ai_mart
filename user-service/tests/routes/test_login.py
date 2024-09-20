from unittest.mock import patch, AsyncMock

from app import settings
from app.utils import create_reset_token
from fastapi.testclient import TestClient
import json

from app.crud.user_crud import create_user

def test_access_token(client: TestClient) -> None:
    login_data = {
        "username":settings.FIRST_SUPERUSER,
        "password":settings.FIRST_SUPERUSER_PASWORD
    }
    r = client.post(f"http://127.0.0.1:8009/login/access-token",data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]

def test_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password":"incorrect"
    }
    r = client.post(f"http://127.0.0.1:8009/login/access-token",data=login_data)
    assert r.status_code == 400

def test_password_reset_request_success(client: TestClient, normal_user_token_headers: dict[str, str]) ->None:
    """
    Test successful password reset request where the user exists, 
    database operations are real, and only Kafka producer is mocked.
    """

    # Insert a test user into the database (this assumes you have some session or fixture)
    test_user = create_user(
        session=client,
        email="test@example.com",
        hashed_password="fakehashedpassword"
    )

    # Mock the Kafka producer
    with patch("app.deps.get_kafka_producer", new_callable=AsyncMock) as mock_producer:
        # Mock the send_and_wait method of the producer
        mock_producer.return_value.send_and_wait = AsyncMock(return_value=None)
        
        # Prepare the request data
        data = {
            "email": settings.FIRST_SUPERUSER
        }
        
        # Make the request to the FastAPI endpoint
        response = client.post("http://127.0.0.1:8009/password-reset-request/", json=data,
                               headers=normal_user_token_headers)
        
        # Assert the correct HTTP status
        assert response.status_code == 200
        assert response.json() == {"message": "Password reset link sent"}
        
        # Verify that the Kafka producer's send_and_wait method was called correctly
        mock_producer.return_value.send_and_wait.assert_called_once_with(
            "password_reset_events",
            json.dumps({
                "user_id": test_user.id,
                "email": "test@example.com",
                "message": f"Password reset link: http://127.0.0.1:8009/password-reset?token=mocked_token Note: Ignore this message if you do not request for password reset",
                "subject": "Reset password  confirmation!",
                "notification_type": "email"
            }).encode("utf-8")
        )




def test_password_reset_request_success(client: TestClient):
    """
    Test successful password reset request where the user exists, 
    database operations are real, and only Kafka producer is mocked.
    """

    # Insert a test user into the database (this assumes you have some session or fixture)
    test_user = create_user(
        session=client,
        email="test@example.com",
        hashed_password="fakehashedpassword"
    )

    # Mock the Kafka producer
    with patch("app.dependencies.get_kafka_producer", new_callable=AsyncMock) as mock_producer:
        # Mock the send_and_wait method of the producer
        mock_producer.return_value.send_and_wait = AsyncMock(return_value=None)
        
        # Prepare the request data
        data = {
            "email": "test@example.com"
        }
        
        # Make the request to the FastAPI endpoint
        response = client.post("http://127.0.0.1:8009/password-reset-request/", json=data)
        
        # Assert the correct HTTP status
        assert response.status_code == 200
        assert response.json() == {"message": "Password reset link sent"}
        
        # Verify that the Kafka producer's send_and_wait method was called correctly
        mock_producer.return_value.send_and_wait.assert_called_once_with(
            "password_reset_events",
            json.dumps({
                "user_id": test_user.id,
                "email": "test@example.com",
                "message": f"Password reset link: http://127.0.0.1:8009/password-reset?token=mocked_token Note: Ignore this message if you do not request for password reset",
                "subject": "Reset password  confirmation!",
                "notification_type": "email"
            }).encode("utf-8")
        )


def test_password_reset_request_user_not_found(client: TestClient, normal_user_token_headers: dict[str, str]) ->None:
    """
    Test the case where the email does not exist in the system.
    Actual DB query will occur, Kafka producer is mocked.
    """

    data = {
        "email": "nonexistent@example.com"
    }
    
    # Make the request to the FastAPI endpoint
    response = client.post("http://127.0.0.1:8009/password-reset-request/", json=data,headers=normal_user_token_headers)
    
    # Assert the correct HTTP status and error message
    assert response.status_code == 404
    assert response.json() == {"detail": "Email not found"}

def test_password_reset(client: TestClient, superuser_token_headers: dict[str, str]) ->None:
    token = create_reset_token(email=settings.FIRST_SUPERUSER)
    data = {"token":token,"new_password":"changthis"}
    r = client.post("http://127.0.0.1:8009/password-reset",
                    headers=superuser_token_headers,
                    json=data)
    assert r.status_code == 200
    assert r.json() ==  {"msg": "Password reset successful"}

def test_reset_password_invalid_token(
        client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"token":"invalid","new_password":"changthis"}
    r = client.post(
        "http://127.0.0.1:8009/password-reset",
        headers=superuser_token_headers,
        json=data
    )
    response = r.json()

    assert "detail" in response
    assert r.json_code == 400
    assert response["detail"] == "Invalid or expired token"