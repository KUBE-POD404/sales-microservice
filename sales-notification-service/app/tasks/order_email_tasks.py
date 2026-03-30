from celery import shared_task
from app.services.email_service import send_email
import logging

logger = logging.getLogger(__name__)


# -----------------------------
# Helper: format order items
# -----------------------------
def format_order_items(items: list) -> str:
    if not items:
        return "No items found."

    lines = []
    for item in items:
        lines.append(
            f"- {item['product_name']} | Qty: {item['quantity']} | Price: ₹{item['unit_price']}"
        )

    return "\n".join(lines)


# -----------------------------
# ORDER CREATED
# -----------------------------
@shared_task(
    name="notification.send_order_created_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def send_order_created_email(self, payload):

    logger.info("Processing ORDER_CREATED event", extra={"payload": payload})

    try:
        data = payload["payload"]

        email = data.get("email")
        customer_name = data.get("customer_name", "Customer")
        order_id = data.get("order_id")
        items = data.get("items", [])

        if not email:
            raise ValueError("Missing email in payload")

        formatted_items = format_order_items(items)

        subject = f"Order #{order_id} Created"

        body = f"""
Hello {customer_name},

Your order #{order_id} has been created successfully.

🧾 Order Details:
{formatted_items}

We will notify you once your order is confirmed.

– Opslora Team
"""

        send_email(
            to_email=email,
            subject=subject,
            body=body
        )

        logger.info(
            "ORDER_CREATED email sent",
            extra={"order_id": order_id, "email": email}
        )

    except Exception as e:
        logger.error(f"ORDER_CREATED task failed: {e}", extra={"payload": payload})
        raise


# -----------------------------
# ORDER CONFIRMED
# -----------------------------
@shared_task(
    name="notification.send_order_confirmed_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def send_order_confirmed_email(self, payload):

    logger.info("Processing ORDER_CONFIRMED event", extra={"payload": payload})

    try:
        data = payload["payload"]

        email = data.get("email")
        customer_name = data.get("customer_name", "Customer")
        order_id = data.get("order_id")
        items = data.get("items", [])

        if not email:
            raise ValueError("Missing email in payload")

        formatted_items = format_order_items(items)

        subject = f"Order #{order_id} Confirmed"

        body = f"""
Hello {customer_name},

Great news! 🎉

Your order #{order_id} has been confirmed.

🧾 Order Details:
{formatted_items}

Thank you for choosing Opslora.

– Opslora Team
"""

        send_email(
            to_email=email,
            subject=subject,
            body=body
        )

        logger.info(
            "ORDER_CONFIRMED email sent",
            extra={"order_id": order_id, "email": email}
        )

    except Exception as e:
        logger.error(f"ORDER_CONFIRMED task failed: {e}", extra={"payload": payload})
        raise


# -----------------------------
# ORDER CANCELLED
# -----------------------------
@shared_task(
    name="notification.send_order_cancelled_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def send_order_cancelled_email(self, payload):

    logger.info("Processing ORDER_CANCELLED event", extra={"payload": payload})

    try:
        data = payload["payload"]

        email = data.get("email")
        customer_name = data.get("customer_name", "Customer")
        order_id = data.get("order_id")
        items = data.get("items", [])

        if not email:
            raise ValueError("Missing email in payload")

        formatted_items = format_order_items(items)

        subject = f"Order #{order_id} Cancelled"

        body = f"""
Hello {customer_name},

Your order #{order_id} has been cancelled.

🧾 Order Details:
{formatted_items}

If this was unexpected, please contact support.

– Opslora Team
"""

        send_email(
            to_email=email,
            subject=subject,
            body=body
        )

        logger.info(
            "ORDER_CANCELLED email sent",
            extra={"order_id": order_id, "email": email}
        )

    except Exception as e:
        logger.error(f"ORDER_CANCELLED task failed: {e}", extra={"payload": payload})
        raise