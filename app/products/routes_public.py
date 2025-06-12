from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.products import schemas, crud

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = "id",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    return crud.get_products(db, category, min_price, max_price, sort_by, page, page_size)

@router.get("/search", response_model=List[schemas.ProductOut])
def search_products(keyword: str, db: Session = Depends(get_db)):
    return crud.search_products(db, keyword)

@router.get("/{id}", response_model=schemas.ProductOut)
def product_detail(id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, id)
    if not product:
        return {"error": True, "message": "Product not found", "code": 404}
    return product
