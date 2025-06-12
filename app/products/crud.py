from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.products import models

def get_products(db: Session, category: str = None, min_price: float = None, max_price: float = None, sort_by: str = "id", page: int = 1, page_size: int = 10):
    query = db.query(models.Product)

    if category:
        query = query.filter(models.Product.category == category)
    if min_price:
        query = query.filter(models.Product.price >= min_price)
    if max_price:
        query = query.filter(models.Product.price <= max_price)

    if sort_by in ["price", "name", "id"]:
        query = query.order_by(getattr(models.Product, sort_by))

    return query.offset((page - 1) * page_size).limit(page_size).all()

def search_products(db: Session, keyword: str):
    return db.query(models.Product).filter(
        or_(
            models.Product.name.ilike(f"%{keyword}%"),
            models.Product.description.ilike(f"%{keyword}%")
        )
    ).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()
