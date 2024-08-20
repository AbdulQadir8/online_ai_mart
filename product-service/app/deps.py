from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from fastapi import HTTPException
from app.db_engine import engine
from requests import post, get
from app import settings
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

#Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

def load_error_json(error_message: str) -> str:
    details = json.loads(error_message.text)
    error_details = details.get("detail")
    return error_details


def get_session():
    with Session(engine) as session:
        yield session

from fastapi import HTTPException

from requests.exceptions import ConnectionError, Timeout

def login_for_access_token(form_data):
    url = "http://user-service:8000/login"
    data = {
        "username": form_data.username,
        "password": form_data.password
    }
    try:
        response = session.post(url, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.content)
        return response.json()

    except ConnectionError as ce:
        print(f"Connection Error: {ce}")
        raise HTTPException(status_code=500, detail="Failed to connect to user service.")
    except Timeout as te:
        print(f"Timeout Error: {te}")
        raise HTTPException(status_code=504, detail="The user service timed out.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")



def get_current_user(token: str):
    url = f"{settings.AUTH_SERVER_URL}/api/v1/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)

    print( "AUTHENTICATED_USER_DATA" ,response.json())

    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code, detail=load_error_json(response))