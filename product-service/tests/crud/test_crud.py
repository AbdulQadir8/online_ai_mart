
from app.models.product_model import CreateProduct, UpdateProduct
from app.crud.product_crud import (add_new_product,
                                   get_all_products,
                                   get_product_by_id,
                                   delete_product_by_id,
                                   update_product_by_id,
                                   validate_product_by_id)
from sqlmodel import Session

def test_add_new_product(db: Session):
  name="Fine Bulb"
  description="This is File Bulb"
  price=350
  category="Pin Bulb"
  product_in = CreateProduct(name=name,
                             description=description,
                             price=price,
                             category=category)
  product_created = add_new_product(product_data=product_in,session=db)
  assert product_created.name == name
  assert product_created.description == description

def test_get_all_products(db: Session):
  product1 = CreateProduct(name="Shoes",
                           description="These are shoes",
                           price=1200,
                           category="Sniker")
  product2 = CreateProduct(name="Handfree",
                           description="These are Handfrees of Geuni",
                           price=550,
                           category="Geniun")
  add_new_product(product_data=product1,session=db)
  add_new_product(product_data=product2,session=db)
  all_products = get_all_products(session=db)
  assert len(all_products) > 1
  for product in all_products:
    if product.id == 3:
      assert product.name == "Handfree"

def test_get_product_by_id(db: Session):
  product_in = CreateProduct(name="Book",
                           description="These are the Books",
                           price=550,
                           category="Geniun")
  product = add_new_product(product_data=product_in,session=db)
  db_product = get_product_by_id(product_id=product.id, session=db)
  assert db_product.id == product.id
  assert db_product.name == product.name


def test_get_product_by_id_not_found(db: Session):
  productid = 99999
  response = get_product_by_id(product_id=productid,session=db)
  assert response == None

def test_delete_product_by_id(db: Session):
  product_in = CreateProduct(name="Cottons",
                           description="These are the Cottons",
                           price=450,
                           category="Cheap")
  product = add_new_product(product_data=product_in,session=db)
  product_del = delete_product_by_id(product_id=product.id,session=db)
  assert product_del == {"message": "Product Deleted Successfully"} 

def test_delete_product_by_id_not_found(db: Session):
  productid = 99999
  response = delete_product_by_id(product_id=productid,session=db)
  assert response == None

def test_update_product_by_id(db: Session):
  product_in = CreateProduct(name="Cup",
                          description="These are Cups",
                          price=500,
                          category="Medium")
  db_product = add_new_product(product_data=product_in,session=db)
  product_in = UpdateProduct(price=600)
  response = update_product_by_id(product_id=db_product.id, to_update_product_data=product_in,session=db)
  assert response.id == db_product.id
  assert response.price == db_product.price

def test_update_product_by_id_not_found(db: Session):
  product_in = CreateProduct(name="Charger",
                          description="This is Charger",
                          price=200,
                          category="Medium")
  db_product = add_new_product(product_data=product_in,session=db)
  product_in = UpdateProduct(price=300)
  response = update_product_by_id(product_id=99999, to_update_product_data=product_in,session=db)
  assert response == None

def test_validate_product_by_id(db: Session):
    product_in = CreateProduct(name="Pen",
                          description="This is Pen",
                          price=20,
                          category="Medium")
    product = add_new_product(product_data=product_in,session=db)
    response = validate_product_by_id(product_id=product.id, session=db)
    assert product.id == response.id
    assert product.price == response.price

def test_validate_product_by_id_not_found(db: Session):
  product_id = 99999
  response = validate_product_by_id(product_id=product_id,session=db)
  assert response == None