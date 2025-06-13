from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.products import schemas, crud
from app.core.logger import logger

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
    logger.info(f"Product listing request - Category: {category}, Price: {min_price}-{max_price}, "
                f"Sort: {sort_by}, Page: {page}, Size: {page_size}")
    try:
        products = crud.get_products(db, category, min_price, max_price, sort_by, page, page_size)
        logger.info(f"{len(products)} products returned for page {page}")
        return products
    except Exception as e:
        logger.error(f"Failed to list products: {e}", exc_info=True)
        raise

@router.get("/search", response_model=List[schemas.ProductOut])
def search_products(keyword: str, db: Session = Depends(get_db)):
    logger.info(f"Product search requested with keyword: '{keyword}'")
    try:
        results = crud.search_products(db, keyword)
        logger.info(f"{len(results)} products found for keyword: '{keyword}'")
        return results
    except Exception as e:
        logger.error(f"Search failed for keyword '{keyword}': {e}", exc_info=True)
        raise

@router.get("/{id}", response_model=schemas.ProductOut)
def product_detail(id: int, db: Session = Depends(get_db)):
    logger.info(f"Product detail requested for product ID: {id}")
    product = crud.get_product_by_id(db, id)
    if not product:
        logger.warning(f"Product ID {id} not found")
        return {"error": True, "message": "Product not found", "code": 404}
    logger.info(f"Product found: {product.name} (ID: {product.id})")
    return product
