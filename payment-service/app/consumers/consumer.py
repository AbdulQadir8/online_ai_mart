from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
from fastapi import HTTPException
from app.deps import get_session
from app.db_engine import engine
from datetime import datetime
from fastapi.responses import RedirectResponse
from app.models.payment_model import Payment, Transaction
from app import settings
import logging
logging.basicConfig(level=logging.INFO)

import stripe
stripe.api_key = "sk_test_51PjlvEP3SJXV8PQkTdnMMA06tDTmZ7zktKhp9UvaPohoYDifcemNlip9zQZpTl6P9SShULaTxcN2yfK8o6Nwgznp000coKzVJN"


async def consume_order_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="payment_event_consumer_group",
        auto_offset_reset="earliest",
    )
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await consumer.start()

    try:
        async for message in consumer:
            logging.info("RAW Payment event")
            logging.info(f"Received message on topic {message.topic} at offset {message.offset}")
            logging.info(f"Message Value: {message.value}")

            order_data = json.loads(message.value.decode())
            logging.info(f"Decoded DATA: {order_data}")
            payment_id: int = order_data
        
    
            try:
                with next(get_session()) as session:
                    payment = session.query(Payment).filter(Payment.id == payment_id).first()
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
                    success_url='https://your-site.com/payment-success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url='https://your-site.com/payment-cancel',
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

                # Redirect to Stripe checkout URL
                return RedirectResponse(url=checkout_session.url, status_code=303)
            
            except stripe.error.StripeError as e:
                # Handle Stripe error and mark the transaction as failed
                with next(get_session()) as session:
                    transaction.status = "failed"
                    transaction.updated_at = datetime.utcnow()
                    session.add(transaction)
                    session.commit()

                raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    except Exception as e:
        logging.info(f"Error processing message: {e}")
        # Optionally, handle the exception (e.g., write to a dead-letter queue)           
    finally:
        await consumer.stop()
