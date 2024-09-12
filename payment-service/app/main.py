# main.py
from contextlib import asynccontextmanager
import stripe
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import AsyncGenerator, Annotated
from datetime import datetime
from aiokafka import AIOKafkaProducer
import json
from app.consumers.consumer import consume_order_messages
from app.models.payment_model import Payment, Transaction
from app.db_engine import engine
from sqlmodel import SQLModel, Session
from app.deps import get_kafka_producer, get_session, GetCurrentAdminDep
from app.requests import get_current_user, login_for_access_token
from app.crud.payment_crud import (create_payment, update_payment_status,get_payment,
                                    get_transaction, create_transaction,
                                    update_transaction_status)
from fastapi.middleware.cors import CORSMiddleware
import stripe
stripe.api_key = "sk_test_51PjlvEP3SJXV8PQkTdnMMA06tDTmZ7zktKhp9UvaPohoYDifcemNlip9zQZpTl6P9SShULaTxcN2yfK8o6Nwgznp000coKzVJN"



def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# loop = asyncio.get_event_loop()
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    # task = asyncio.create_task(consume_order_messages("payment_events", 'broker:19092'))
    yield


app = FastAPI(lifespan=lifespan, 
            title="Payment Service API with DB", 
            version="0.0.1",
             servers=[
                        {
                            "url": "http://127.0.0.1:8008", # ADD NGROK URL Here Before Creating GPT Action
                            "description": "Development Server"
                        }
                        ]
            )
# Allow CORS for all origins (for development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"App": "Payment Service"}

@app.post("/login-endpoint", tags=["Wrapper Auth"])
def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
    auth_token = login_for_access_token(form_data)
    return auth_token

@app.post("/create-checkout-session/")
async def create_checkout_session(payment_id: int,
                                  session: Annotated[Session, Depends(get_session)],
                                  producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
                                  user_data: Annotated[str | None, Depends(get_current_user)]):

    # payment_id_json = json.dumps(payment_id).encode("utf-8")
    # print(f"Payment Id Json: {payment_id_json}")
    # #Produce Message
    # await producer.send_and_wait("payment_events",payment_id_json)
    # return {"message":"Payment Initiated"}

    payment = session.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Create a new Transaction for this payment attempt
    transaction = Transaction(
        payment_id=payment_id,
        status="initiated",  # Initial status of the transaction
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(transaction)
    session.commit()  # Commit transaction creation to DB
    session.refresh(transaction)
    try:
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': payment.currency,
                    'product_data': {
                        'name': f'Order {payment.order_id}',
                    },
                    'unit_amount': int(payment.amount * 100),  # Amount in cents
                },
                'quantity': 1
            }],
            mode='payment',
            success_url='http://127.0.0.1:8008/docs',
            cancel_url='http://127.0.0.1:8008/docs',
            metadata={
                'user_id': payment.user_id,
                'payment_id': payment.id,
                'transaction_id': transaction.id  # Track which transaction this corresponds to
            }
        )
        
        # Update the Payment and Transaction records with Stripe details
        payment.stripe_checkout_session_id = checkout_session.id
        payment.updated_at = datetime.utcnow()  # Track the last update time for payment
        
        transaction.status = "processing"  # Mark transaction as processing
        transaction.updated_at = datetime.utcnow()
        session.add(payment)
        session.add(transaction)
        session.commit()

        # Prepare the message for Kafka (to send email notification)
        email_event = {
            "user_id": user_data["id"],
            "email": user_data["email"],  
            "message": f"Your payment for Order #{payment.order_id} is now processing.",
            "subject": "Pament processing!",
            "notification_type":"email"
        }
        # Serialize the event data to JSON
        email_event_json = json.dumps(email_event).encode("utf-8")

        # Produce the event to Kafka for email notification
        await producer.send_and_wait("order_notification_events", email_event_json)
        print(f"Sent email notification event for Payment ID: {payment_id}")

        # Redirect to Stripe checkout URL
        return checkout_session.url
    
    except stripe.error.StripeError as e:
        # Handle Stripe error and mark the transaction as failed
        transaction.status = "failed"
        transaction.updated_at = datetime.utcnow()
        session.add(transaction)
        session.commit()

        # Send failure email event via Kafka
        email_event = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "message": f"Your payment for Order #{payment.order_id} failed.",
            "subject": "Payment failed!",
            "notification_type":"email"
        }
        email_event_json = json.dumps(email_event).encode("utf-8")
        await producer.send_and_wait("order_notification_events", email_event_json)
        print(f"Sent email notification event for failed Payment ID: {payment_id}")

        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")



@app.post("/payments/", response_model=Payment, dependencies=[GetCurrentAdminDep])
def create_payment_endpoint(payment_data: Payment, session: Session = Depends(get_session)):
    return create_payment(session, payment_data)

@app.get("/payments/{payment_id}", response_model=Payment, dependencies=[GetCurrentAdminDep])
def get_payment_endpoint(payment_id: int, session: Session = Depends(get_session)):
    payment = get_payment(session, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.patch("/payments/{payment_id}", response_model=Payment, dependencies=[GetCurrentAdminDep])
def update_payment_status_endpoint(payment_id: int, status: str, session: Session = Depends(get_session)):
    payment = update_payment_status(session, payment_id, status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment



@app.post("/transactions/", response_model=Transaction, dependencies=[GetCurrentAdminDep])
def create_transaction_endpoint(transaction_data: Transaction, session: Session = Depends(get_session)):
    return create_transaction(session, transaction_data)

@app.get("/transactions/{transaction_id}", response_model=Transaction, dependencies=[GetCurrentAdminDep])
def get_transaction_endpoint(transaction_id: int, session: Session = Depends(get_session)):
    transaction = get_transaction(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.patch("/transactions/{transaction_id}", response_model=Transaction, dependencies=[GetCurrentAdminDep])
def update_transaction_status_endpoint(transaction_id: int, status: str, session: Session = Depends(get_session)):
    transaction = update_transaction_status(session, transaction_id, status)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction




# Stripe webhook secret
# webhook_secret = "your-webhook-signing-secret"

# @router.post("/stripe/webhook")
# async def stripe_webhook(request: Request, session: Session = Depends(get_session), producer = Depends(get_kafka_producer)):
#     payload = await request.body()
#     sig_header = request.headers.get("stripe-signature")

#     try:
#         # Verify webhook signature
#         event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail="Invalid payload")
#     except stripe.error.SignatureVerificationError as e:
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     # Handle successful payment
#     if event['type'] == 'checkout.session.completed':
#         session_id = event['data']['object']['id']
#         metadata = event['data']['object']['metadata']

#         payment = session.query(Payment).filter_by(stripe_checkout_session_id=session_id).first()
#         transaction = session.query(Transaction).filter_by(id=metadata['transaction_id']).first()

#         if payment and transaction:
#             payment.status = "success"
#             transaction.status = "success"
#             session.commit()

#             # Notify user via Kafka event (e.g., sending success email)
#             email_event = {
#                 "user_id": payment.user_id,
#                 "email": "user@example.com",  # Assuming email is available
#                 "message": f"Your payment for Order {payment.order_id} was successful.",
#                 "status": "success"
#             }
#             await producer.send_and_wait("payment_events", json.dumps(email_event).encode('utf-8'))
#             print(f"Payment success notification sent for Payment ID: {payment.id}")

#     # Handle failed payment
#     if event['type'] == 'payment_intent.payment_failed':
#         session_id = event['data']['object']['id']
#         metadata = event['data']['object']['metadata']

#         payment = session.query(Payment).filter_by(stripe_checkout_session_id=session_id).first()
#         transaction = session.query(Transaction).filter_by(id=metadata['transaction_id']).first()

#         if payment and transaction:
#             payment.status = "failed"
#             transaction.status = "failed"
#             session.commit()

#             # Notify user via Kafka event (e.g., sending failure email)
#             email_event = {
#                 "user_id": payment.user_id,
#                 "email": "user@example.com",
#                 "message": f"Your payment for Order {payment.order_id} failed.",
#                 "status": "failed"
#             }
#             await producer.send_and_wait("payment_events", json.dumps(email_event).encode('utf-8'))
#             print(f"Payment failure notification sent for Payment ID: {payment.id}")

#     return {"status": "success"}
