# from sqlmodel import Session

# from app.models.payment_model import CreatePayment
# from app.crud.payment_crud import create_payment,get_payment

# def test_create_payment(db: Session):
#     payment_data =CreatePayment(order_id=2,
#                                 user_id=4,
#                                 amount=200,
#                                 currency='usd',
#                                 status="pending")
#     data = create_payment(session=db, payment_data=payment_data)
#     assert data
#     assert data.amount == 200

# def test_get_payment(db: Session):
#     payment_data =CreatePayment(order_id=3,
#                                 user_id=5,
#                                 amount=300,
#                                 currency='usd',
#                                 status="completed")
#     data = create_payment(session=db, payment_data=payment_data)
#     db_data = get_payment(session=db,payment_id=data.id)
#     assert db_data.amount == 300
#     assert db_data.status == "completed"
from app.models.payment_model import CreatePayment
from app.crud.payment_crud import (create_payment,
                                   get_payment,
                                   update_payment_status,
                                   create_transaction,
                                   get_transaction,
                                   update_transaction_status,
                                   delete_payment,
                                   delete_transaction)
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.payment_model import CreatePayment, CreateTransaction
from sqlmodel import Session
from datetime import datetime, timezone


def test_create_payment(db: Session):
    payment_data = CreatePayment(
        order_id=2,
        user_id=4,
        amount=200,
        currency='usd',
        status="pending"
    )
    payment = create_payment(session=db, payment_data=payment_data)
    
    assert payment
    assert payment.amount == 200
    assert payment.status == "pending"
    assert payment.currency == "usd"
    assert payment.created_at <= datetime.utcnow()  # Ensure timestamp is set


def test_get_payment(db: Session):
    payment_data = CreatePayment(
        order_id=3,
        user_id=5,
        amount=300,
        currency='usd',
        status="completed"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)
    retrieved_payment = get_payment(session=db, payment_id=created_payment.id)
    
    assert retrieved_payment
    assert retrieved_payment.amount == 300
    assert retrieved_payment.status == "completed"
    assert retrieved_payment.currency == "usd"

def test_get_payment_not_found(db: Session):
    fake_payment_id=99999
    retrieved_payment = get_payment(session=db, payment_id=fake_payment_id)
    
    assert retrieved_payment == None


def test_update_payment_status(db: Session):
    payment_data = CreatePayment(
        order_id=4,
        user_id=6,
        amount=400,
        currency='eur',
        status="pending"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)

    updated_payment = update_payment_status(session=db, payment_id=created_payment.id, status="completed")

    assert updated_payment
    assert updated_payment.status == "completed"
    assert updated_payment.updated_at >= created_payment.updated_at  # Ensure updated_at was changed

def test_update_payment_status_not_found(db: Session):
    fake_payment_id=99999
    updated_payment = update_payment_status(session=db, payment_id=fake_payment_id, status="completed")
    
    assert updated_payment == None

def test_delete_payment(db: Session):
    payment_data = CreatePayment(
        order_id=4,
        user_id=6,
        amount=400,
        currency='eur',
        status="pending"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)
    response = delete_payment(session=db,payment_id=created_payment.id)
    assert response ==  {"message":"Payment deleted successfully"}

def test_delete_payment_not_found(db: Session):
    fake_payment_id=99999
    response = delete_payment(session=db, payment_id=fake_payment_id)
    
    assert response == None


def test_create_transaction(db: Session):
    # First create a payment record that the transaction can reference
    payment_data = CreatePayment(
        order_id=1,
        user_id=1,
        amount=100,
        currency='usd',
        status="pending"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)

    # Now create a transaction using the payment_id from the created payment
    transaction_data = CreateTransaction(
        payment_id=created_payment.id,  # Ensure the payment_id is valid
        status="initiated"
    )
    transaction = create_transaction(session=db, transaction_data=transaction_data)
    
    assert transaction
    assert transaction.payment_id == created_payment.id
    assert transaction.status == "initiated"
    assert transaction.created_at <= datetime.utcnow()  # Ensure timestamp is set

def test_get_transaction(db: Session):
    # First create a payment record that the transaction can reference
    payment_data = CreatePayment(
        order_id=1,
        user_id=1,
        amount=100,
        currency='usd',
        status="pending"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)

    # Now create a transaction using the payment_id from the created payment
    transaction_data = CreateTransaction(
        payment_id=created_payment.id,  # Ensure the payment_id is valid
        status="initiated"
    )
    created_transaction = create_transaction(session=db, transaction_data=transaction_data)

    retrieved_transaction = get_transaction(session=db, transaction_id=created_transaction.id)
    
    assert retrieved_transaction
    assert retrieved_transaction.payment_id == created_payment.id
    assert retrieved_transaction.status == "initiated"

def test_get_transaction_not_found(db: Session):
    fake_transaction_id=99999
    retrieved_transaction = get_transaction(session=db, transaction_id=fake_transaction_id)
    
    assert retrieved_transaction == None

def test_update_transaction_status(db: Session):
    # First create a payment record that the transaction can reference
    payment_data = CreatePayment(
        order_id=1,
        user_id=1,
        amount=100,
        currency='usd',
        status="pending"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)

    # Now create a transaction using the payment_id from the created payment
    transaction_data = CreateTransaction(
        payment_id=created_payment.id,  # Ensure the payment_id is valid
        status="initiated"
    )
    created_transaction = create_transaction(session=db, transaction_data=transaction_data)

    updated_transaction = update_transaction_status(
        session=db, transaction_id=created_transaction.id, status="completed"
    )

    assert updated_transaction
    assert updated_transaction.status == "completed"
    assert updated_transaction.updated_at >= created_transaction.updated_at  # Ensure updated_at was updated
    

def test_update_transaction_status_not_found(db: Session):
    fake_transaction_id=99999
    updated_transaction = update_transaction_status(session=db, transaction_id=fake_transaction_id, status="completed")
    
    assert updated_transaction == None

def test_delete_transaction(db: Session):
    # First create a payment record that the transaction can reference
    payment_data = CreatePayment(
        order_id=4,
        user_id=5,
        amount=500,
        currency='usd',
        status="completed"
    )
    created_payment = create_payment(session=db, payment_data=payment_data)
    transaction_data = CreateTransaction(
        payment_id=created_payment.id,  # Ensure the payment_id is valid
        status="initiated"
    )
    created_transaction = create_transaction(session=db, transaction_data=transaction_data)

    response = delete_transaction(session=db, transaction_id=created_transaction.id)
    assert response == {"message":"Transaction deleted successfully"}

def test_delete_transaction_not_found(db: Session):
    fake_transaction_id=99999
    response = delete_transaction(session=db, transaction_id=fake_transaction_id)
    
    assert response == None