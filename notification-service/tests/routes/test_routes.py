from fastapi.testclient import TestClient
from app.models.notification_model import Notification,NotificationType
from sqlmodel import Session

def test_create_notification(client: TestClient):
    data = {
        "user_id": 1,
        "email":"aq98123@gmail.com",
        "message": "You Order will be Delivered Next Month",
    }
    response = client.post("http://notification-service/notifications/",
                           json=data)
    assert response.status_code == 200
    assert response.json() == {"status": "Order Notification enqueued"}

def test_get_notification_status(client: TestClient, db: Session):
    new_notification = Notification(id=2,
                            user_id=2,
                            notification_type=NotificationType.EMAIL,
                            message="Your payment for Order #1 is now processing.")
    db.add(new_notification)
    db.commit()
    notification_id = new_notification.id
    response = client.get(f"http://notification-service/notifications/{notification_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["user_id"] == 2
    assert data["message"] == "Your payment for Order #1 is now processing."