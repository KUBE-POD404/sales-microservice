from datetime import datetime, timezone
from sqlalchemy.orm import Session
import os

from app.models.order import Order
from app.models.order_item import OrderItem

from app.exceptions.custom_exceptions import NotFoundException, ConflictException
from app.utils.service_client import authenticated_get

from app.core.logging_config import get_logger


from app.tasks.notification_tasks import (
    send_order_created_notification,
    send_order_confirmed_notification,
    send_order_cancelled_notification
)

logger = get_logger(__name__)

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL")


def validate_customer(customer_id: int, auth_header: str):
    response = authenticated_get(
        f"{CUSTOMER_SERVICE_URL}/customers/{customer_id}",
        auth_header
    )

    if response.status_code != 200:
        raise NotFoundException("Customer not found")


def create_order(
    db: Session,
    customer_id: int,
    items: list,
    organization_id: int,
    created_by_user_id: int,
    auth_header: str
) -> Order:

    logger.info(f"Creating order for customer {customer_id}")

    validate_customer(customer_id, auth_header)

    order = Order(
        organization_id=organization_id,
        customer_id=customer_id,
        status="CREATED",
        created_by_user_id=created_by_user_id,
        created_at=datetime.now(timezone.utc),
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
        )

    db.commit()

    logger.info(f"Order created with ID {order.id}")

    # ✅ Async event (Celery)
    send_order_created_notification.delay({
        "order_id": order.id,
        "customer_id": customer_id,
        "organization_id": organization_id
    })

    return get_order(db, order.id, organization_id)


def get_order(db: Session, order_id: int, organization_id: int) -> Order:
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.organization_id == organization_id
        )
        .first()
    )

    if not order:
        raise NotFoundException("Order not found")

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()

    order.items = items
    order.total = sum(item.quantity * item.unit_price for item in items)

    return order


def list_orders(db: Session, organization_id, offset=0, limit=15, status=None, customer_id=None):
    query = db.query(Order).filter(Order.organization_id == organization_id)

    if status:
        query = query.filter(Order.status == status)

    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    orders = (
        query.order_by(Order.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    for order in orders:
        items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        order.items = items
        order.total = sum(item.quantity * item.unit_price for item in items)

    return orders


def update_order(db: Session, order_id: int, organization_id: int, items: list):
    order = get_order(db, order_id, organization_id)

    if order.status != "CREATED":
        raise ConflictException("Only CREATED orders can be updated")

    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()

    for item in items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
        )

    db.commit()

    return get_order(db, order.id, organization_id)


def confirm_order(db: Session, order_id: int, organization_id: int):
    order = get_order(db, order_id, organization_id)

    if order.status != "CREATED":
        raise ConflictException("Only CREATED orders can be confirmed")

    order.status = "CONFIRMED"
    db.commit()
    db.refresh(order)

    logger.info(f"Order confirmed {order.id}")

    send_order_confirmed_notification.delay({
        "order_id": order.id
    })

    return order


def cancel_order(db: Session, order_id: int, organization_id: int):
    order = get_order(db, order_id, organization_id)

    if order.status == "CONFIRMED":
        raise ConflictException("Confirmed orders cannot be cancelled")

    order.status = "CANCELLED"
    db.commit()
    db.refresh(order)

    logger.info(f"Order cancelled {order.id}")

    send_order_cancelled_notification.delay({
        "order_id": order.id
    })

    return order