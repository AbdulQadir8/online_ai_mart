from sqlmodel import Session, select
from app.models.payment_model import Payment, Transaction
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
import os
import stripe
# Set the Stripe API key
stripe.api_key = "sk_test_51PjlvEP3SJXV8PQkTdnMMA06tDTmZ7zktKhp9UvaPohoYDifcemNlip9zQZpTl6P9SShULaTxcN2yfK8o6Nwgznp000coKzVJN"

def create_payment(session: Session, payment_data: Payment) -> Payment:
    payment = payment_data
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def get_payment(session: Session, payment_id: int) -> Payment | None:
    return session.get(Payment, payment_id)

def update_payment_status(session: Session, payment_id: int, status: str) -> Payment | None:
    payment = session.get(Payment, payment_id)
    if payment:
        payment.status = status
        payment.updated_at = datetime.utcnow()
        session.add(payment)
        session.commit()
        session.refresh(payment)
    return payment

# Transaction CRUD operations
def create_transaction(session: Session, transaction_data: Transaction) -> Transaction:
    transaction = transaction_data
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def get_transaction(session: Session, transaction_id: int) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def update_transaction_status(session: Session, transaction_id: int, status: str) -> Transaction | None:
    transaction = session.get(Transaction, transaction_id)
    if transaction:
        transaction.status = status
        transaction.updated_at = datetime.utcnow()
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
    return transaction




def create_checkout_session(payment_id: int, session: Session):
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
                'quantity': 1,
                'metadata': {
                    'user_id': payment.user_id,
                    'payment_id': payment.id
                    }
            }],
            mode='payment',
            success_url='http://127.0.0.1:8008/docs',
            cancel_url='http://127.0.0.1:8007/docs',
        )
        
        # Update Payment Record
        payment.stripe_checkout_session_id = checkout_session.id
        session.add(payment)
        session.commit()
        return RedirectResponse(checkout_session.url)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
