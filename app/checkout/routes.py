from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import user_required
from app.cart.models import Cart as CartItem
from app.orders.models import Order, OrderItem
from app.products.models import Product
from app.core.logger import logger

router = APIRouter(prefix="/checkout", tags=["Checkout"])

@router.post("/")
def checkout(db: Session = Depends(get_db), user=Depends(user_required)):
    logger.info(f"Checkout initiated by user {user.id}")
   
    cart_items = db.query(CartItem).filter_by(user_id=user.id).all()
    if not cart_items:
        logger.warning(f"Checkout failed: Cart is empty for user {user.id}")
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0
    order_items = []

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            logger.warning(
                f"Checkout aborted: Product ID {item.product_id} unavailable or insufficient stock (User: {user.id})"
            )
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
        db.refresh(order)
        logger.info(f"Order created successfully (Order ID: {order.id}, User: {user.id}, Total: {total_amount})")
    except Exception as e:
        db.rollback()
        logger.error(f"Checkout failed during order creation for user {user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database commit failed")


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

    logger.info(f"Checkout completed: Cart cleared and items added to order (User: {user.id}, Order ID: {order.id})")
    return {"detail": "Checkout complete", "order_id": order.id, "total": total_amount}
