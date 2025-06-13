from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import user_required
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderOut, OrderDetailOut, OrderItemOut
from typing import List
from app.core.logger import logger

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderOut])
def get_order_history(db: Session = Depends(get_db), user=Depends(user_required)):
   logger.info(f"User {user.id} requested their order history")
   try:
        orders = db.query(Order).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
        logger.info(f"{len(orders)} orders retrieved for user {user.id}")
        return orders
   except Exception as e:
        logger.error(f"Failed to retrieve order history for user {user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not fetch order history")

@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order_details(order_id: int, db: Session = Depends(get_db), user=Depends(user_required)):
    logger.info(f"User {user.id} requested details for order {order_id}")
    try:
        order = db.query(Order).filter_by(id=order_id, user_id=user.id).first()
        if not order:
            logger.warning(f"Order {order_id} not found or unauthorized access by user {user.id}")
            raise HTTPException(status_code=404, detail="Order not found")

        order_items = db.query(OrderItem).filter_by(order_id=order.id).all()
        logger.info(f"Order {order_id} retrieved with {len(order_items)} items for user {user.id}")
        return {
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": order_items
        }
    except Exception as e:
        logger.error(f"Error fetching order {order_id} for user {user.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not fetch order details")
