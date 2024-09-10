from app.utils import send_email
from app.models.notification_model import NotificationType, NotificationStatus, Notification
from aiokafka import AIOKafkaProducer
import logging
logging.basicConfig(level=logging.INFO)
from sqlmodel import Session
from app.db_engine import engine


#Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()



def get_session():
    with Session(engine) as session:
        yield session

async def process_notification(event_data: dict):
    # Assuming event_data contains 'user_id', 'message', 'notification_type'
    logging.info(f"Event_DATA:{event_data}")
    user_id = event_data['user_id']
    recipient_email = event_data['email']
    message = event_data['message']
    subject = event_data["subject"]
    notification_type = event_data['notification_type']
    
    
    logging.info("Database Session Started")
    with next(get_session()) as session:
        notification = Notification(user_id=user_id, notification_type=notification_type, message=message)
        session.add(notification)
        session.commit()
        logging.info(f"Data Commited:{notification}")

        logging.info("Send Email")
        #Send Email
        if notification_type == NotificationType.EMAIL:
            try:
                await send_email(user_id, recipient_email, message, subject)
                notification.status = NotificationStatus.SENT
                logging.info("Email sent Successfully")
            except Exception as e:
                notification.status = NotificationStatus.FAILED
        session.add(notification)
        session.commit()