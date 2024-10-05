from sqlmodel import Session
from app.crud.order_crud import add_new_order, get_all_orders, get_single_order, delete_single_order
from app.models.order_model import Order

def test_add_new_order(db: Session) ->None:
    user_id = 3
    status = "Processing"
    total_amount = 100
    order_in = Order(user_id=user_id,status=status,total_amount=total_amount)
    order = add_new_order(order=order_in,session=db)
    assert order.user_id == 3
    assert order.status == "Processing"

def test_get_all_orders(db: Session) ->None:
    user_id = 3
    status = "Processing"
    total_amount = 100
    order_in = Order(user_id=user_id,status=status,total_amount=total_amount)
    order1 = add_new_order(order=order_in,session=db)
    user_id = 4
    status = "Completed"
    total_amount = 100
    order_in = Order(user_id=user_id,status=status,total_amount=total_amount)
    order2 = add_new_order(order=order_in,session=db)
    orders = get_all_orders(session=db)
    assert len(orders) > 1

def test_get_single_order(db: Session) ->None:
    user_id = 5
    status = "Processing"
    total_amount = 100
    order_in = Order(user_id=user_id,status=status,total_amount=total_amount)
    order = add_new_order(order=order_in,session=db)
    order_id = order.id
    db_order = get_single_order(order_id=order_id,session=db)
    assert db_order
    assert db_order.id == order_id

def test_get_single_order_not_found(db: Session) ->None:
    order_id = 99999
    db_order = get_single_order(order_id=order_id,session=db)
    assert db_order is None

def test_delete_single_order(db: Session) ->None:
    user_id = 5
    status = "Processing"
    total_amount = 100
    order_in = Order(user_id=user_id,status=status,total_amount=total_amount)
    order = add_new_order(order=order_in,session=db)
    order_id = order.id
    order_deleted = delete_single_order(order_id=order_id,session=db)
    assert order_deleted["message"] == "Order deleted successfully"

def test_delete_single_order_not_found(db: Session) ->None:
    order_id = 99999
    order_deleted = delete_single_order(order_id=order_id,session=db)
    assert order_deleted is None