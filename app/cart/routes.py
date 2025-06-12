from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.cart import schemas
from app.products.models import Product
from app.cart.models import Cart as CartItem
from app.core.dependencies import user_required

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=schemas.CartOut)
def add_to_cart(data: schemas.CartAdd, db: Session = Depends(get_db), user=Depends(user_required)):
   
    print("Incoming request:", data)
    print("Authenticated user:", user)
   
    # check if procduct is available
    product = db.query(Product).filter(Product.id == data.product_id).first()
    print("Queried product:", product)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # check if a product is already in cart
    cart_item = db.query(CartItem).filter_by(user_id=user.id, product_id=data.product_id).first()
    if cart_item:
        cart_item.quantity += data.quantity
    else:
        cart_item = CartItem(user_id=user.id, product_id=data.product_id, quantity=data.quantity)
       
        db.add(cart_item)

    try:
        db.commit()
    except Exception as e:   
        db.rollback()
        print("Commit failed:", str(e))
        raise HTTPException(status_code=500, detail="Database commit failed")

    db.refresh(cart_item)
    return cart_item

@router.get("/", response_model=list[schemas.CartOut])
def view_cart(db: Session = Depends(get_db), user=Depends(user_required)):
    return db.query(CartItem).filter_by(user_id=user.id).all()


@router.put("/{product_id}", response_model=schemas.CartOut)
def update_cart_quantity(
    product_id: int,
    data: schemas.CartUpdate,
    db: Session = Depends(get_db),
    user=Depends(user_required)
):
    # check if item is present in cart
    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if data.quantity <= 0:
        db.delete(item)
        db.commit()
        return {"detail": "Item removed from cart due to zero quantity"}

    # check product's stock
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    #update the qunatity
    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), user=Depends(user_required)):
    item = db.query(CartItem).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(item)
    db.commit()
    return {"detail": "Item removed from cart"}
