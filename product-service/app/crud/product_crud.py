from typing import Any
from sqlmodel import Session, select
from app.models.product_model import Product, CreateProduct, UpdateProduct

#Add a New Product to the Database
def add_new_product(product_data: CreateProduct, session: Session):
    print("Adding Product to Database")
    product = Product.model_validate(product_data)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# Get All Products from the Database
def get_all_products(session: Session) ->Any:
    all_products = session.exec(select(Product)).all()
    return all_products


# Get a Product by ID
def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        return None
    return product

# Delete Product by ID
def delete_product_by_id(product_id: int, session: Session):
    #Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        return None
    #Step 2: Delete the Product
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted Successfully"}

# Update Product by ID
def update_product_by_id(product_id: int, to_update_product_data:UpdateProduct, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        return None
    #Step 2: Update the Product
    dict_data = to_update_product_data.model_dump(exclude_unset=True)
    update_data = {k: v for k, v in dict_data.items() if v is not None}
    print(f"Unique Data: {update_data}")
        
    # Update product using the filtered data
    for key, value in update_data.items():
        setattr(product, key, value)
        
    session.add(product)
    session.commit()
    session.refresh(product)  # Refresh to get updated data from DB
    print("Updated product:", product)  # Debugging statement


    return product

# Validate Product by ID
def validate_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        return None
    return product