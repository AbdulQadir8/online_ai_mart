from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.order_model import Order, OrderItem
import logging 
logging.basicConfig(level=logging.INFO)


# Add a new order to the Database
def add_new_order(order: Order, session: Session):
    logging.info("Adding new order to database")
    session.add(order)
    session.commit()
    session.refresh(order)


# Get all orders from database
def get_all_orders(session: Session):
    logging.info("Geting all orders from database")
    orders = session.exec(select(Order)).all()
    return orders

# Get order by id
def get_single_order(order_id: int, session: Session):
    logging.info("Geting order by id")
    order = session.get(Order,order_id).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order not found with id:{order_id}")
    return order


#Delete Order by id
def delete_single_order(order_id: int, session: Session):
    logging.info("Deleting order by id")
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404,detail=f"Order not found with id:{order_id}")
    session.delete(order)
    session.commit()
    return {"message":"Order deleted successfully"}

#Update Order by id
# def update_order(order_id: int, update_order: OrderUpdate)


