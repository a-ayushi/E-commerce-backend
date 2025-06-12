from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import user_required
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderOut, OrderDetailOut, OrderItemOut
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderOut])
def get_order_history(db: Session = Depends(get_db), user=Depends(user_required)):
    orders = db.query(Order).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order_details(order_id: int, db: Session = Depends(get_db), user=Depends(user_required)):
    order = db.query(Order).filter_by(id=order_id, user_id=user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.query(OrderItem).filter_by(order_id=order.id).all()
    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": order_items
    }
