from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.products import models, schemas
from app.core.database import get_db
from app.core.dependencies import admin_required
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Response

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])


@router.post("/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db),
                   admin: dict = Depends(admin_required)):
    
    try:
        product_data = product.dict()
        product_data["image_url"] = str(product.image_url) if product.image_url else None  #  Convert HttpUrl to str
        product_data["owner_id"] = admin.id  
       
        db_product = models.Product(**product_data)
        db.add(db_product)
      
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database commit failed")
        
        db.refresh(db_product)
        return db_product
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
  

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), 
                  admin: dict = Depends(admin_required)):
    return db.query(models.Product.owner_id == admin.id).offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), 
                admin: dict = Depends(admin_required)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
   
    if product.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Not authorized to see this product")

    return product

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, updated: schemas.ProductUpdate, db: Session = Depends(get_db), 
                   admin: dict = Depends(admin_required)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")
    
    for key, value in updated.dict().items():
        if key == "image_url" and value is not None:
            value = str(value)
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db), 
                   admin: dict = Depends(admin_required)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.owner_id != admin.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    db.delete(product)
    db.commit()
    
    return {"detail": "Product deleted"}


