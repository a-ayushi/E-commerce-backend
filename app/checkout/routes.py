from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import user_required
from app.cart.models import Cart as CartItem
from app.orders.models import Order, OrderItem
from app.products.models import Product

router = APIRouter(prefix="/checkout", tags=["Checkout"])

@router.post("/")
def checkout(db: Session = Depends(get_db), user=Depends(user_required)):
    cart_items = db.query(CartItem).filter_by(user_id=user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0
    order_items = []

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Product ID {item.product_id} is unavailable or out of stock")
        
        # Deduct stock
        product.stock -= item.quantity

        total_amount += product.price * item.quantity
        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_purchase": product.price
        })

    # Create Order
    order = Order(user_id=user.id, total_amount=total_amount, status="paid")
    db.add(order)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print("Commit failed:", str(e))
        raise HTTPException(status_code=500, detail="Database commit failed")

    db.refresh(order)

    # Add OrderItems
    for item in order_items:
        db_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price_at_purchase=item["price_at_purchase"]
        )
        db.add(db_item)

    # Clear Cart
    db.query(CartItem).filter_by(user_id=user.id).delete()
    db.commit()

    return {"detail": "Checkout complete", "order_id": order.id, "total": total_amount}
