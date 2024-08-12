# main.py
from contextlib import asynccontextmanager
import stripe
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer
import asyncio
from app.consumers.consumer import consume_order_messages
from app.models.payment_model import Payment, Transaction
from app.db_engine import engine
from sqlmodel import SQLModel, Session
from app.deps import get_kafka_producer, get_session
from app.crud.payment_crud import (create_payment, update_payment_status,get_payment,
                                    get_transaction, create_transaction,
                                    update_transaction_status, create_checkout_session)
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
    task = asyncio.create_task(consume_order_messages("InventoryReserved", 'broker:19092'))
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

@app.post("/create-checkout-session/")
def create_checkout_session(payment_id: int, session: Session = Depends(get_session)):
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
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
            success_url='https://www.youtube.com/watch?v=QxcGFmVdcFQ',
            cancel_url='https://www.youtube.com/watch?v=QxcGFmVdcFQ',
            metadata= {
                    'user_id': payment.user_id,
                    'payment_id': payment.id
                    }
        )
     
        # Update Payment Record
        payment.stripe_checkout_session_id = checkout_session.id
        session.add(payment)
        session.commit()
        return RedirectResponse(url=checkout_session.url, status_code=303)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))





@app.post("/payments/", response_model=Payment)
def create_payment_endpoint(payment_data: Payment, session: Session = Depends(get_session)):
    return create_payment(session, payment_data)

@app.get("/payments/{payment_id}", response_model=Payment)
def get_payment_endpoint(payment_id: int, session: Session = Depends(get_session)):
    payment = get_payment(session, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.patch("/payments/{payment_id}", response_model=Payment)
def update_payment_status_endpoint(payment_id: int, status: str, session: Session = Depends(get_session)):
    payment = update_payment_status(session, payment_id, status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment



@app.post("/transactions/", response_model=Transaction)
def create_transaction_endpoint(transaction_data: Transaction, session: Session = Depends(get_session)):
    return create_transaction(session, transaction_data)

@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction_endpoint(transaction_id: int, session: Session = Depends(get_session)):
    transaction = get_transaction(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.patch("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction_status_endpoint(transaction_id: int, status: str, session: Session = Depends(get_session)):
    transaction = update_transaction_status(session, transaction_id, status)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
