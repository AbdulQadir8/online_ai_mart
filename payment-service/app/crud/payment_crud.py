from sqlmodel import Session, select
from app.models.payment_model import (Payment,
                                      Transaction,
                                      CreatePayment,
                                      CreateTransaction)
from datetime import datetime

def create_payment(session: Session, payment_data: CreatePayment) -> Payment:
    payment = Payment.model_validate(payment_data)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def get_payment(session: Session, payment_id: int) -> Payment | None:
    payment = session.get(Payment, payment_id)
    if not payment:
        return None
    return payment

def update_payment_status(session: Session, payment_id: int, data: dict) -> Payment | None:
    payment = session.get(Payment, payment_id)
    if payment:
        payment.status = data["status"]
        payment.updated_at = datetime.utcnow()
        session.add(payment)
        session.commit()
        session.refresh(payment)
    return payment

def delete_payment(session: Session, payment_id: int)-> dict | None:
    retrieved_payment = session.exec(select(Payment).where(Payment.id == payment_id)).one_or_none()
    if not retrieved_payment:
        return None
    session.delete(retrieved_payment)
    session.commit()
    return {"message":"Payment deleted successfully"}

def create_transaction(session: Session, transaction_data: CreateTransaction) -> Transaction:
    transaction = Transaction.model_validate(transaction_data)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def get_transaction(session: Session, transaction_id: int) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def update_transaction_status(session: Session, transaction_id: int, data: dict) -> Transaction | None:
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        return None
    transaction.status = data["status"]
    transaction.updated_at = datetime.utcnow()
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def delete_transaction(session: Session, transaction_id: int) ->dict | None:
    retrieved_transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).one_or_none()
    if not retrieved_transaction:
        return retrieved_transaction
    session.delete(retrieved_transaction)
    session.commit()
    return {"message":"Transaction deleted successfully"}