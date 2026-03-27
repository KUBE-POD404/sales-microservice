from app.core.celery_app import celery
from app.services.email_service import send_email
import logging

logger = logging.getLogger(__name__)


@celery.task(
    name="notification.send_signup_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def send_signup_email(self, payload):

    logger.info(f"Received signup event: {payload}")

    try:
        data = payload["data"]

        subject = "Welcome to Opslora "

        body = f"""
Hello,

Your organization "{data['organization_name']}" has been created successfully.

You can now start managing your customers, orders, invoices, payments, and inventory in one place.

Welcome to Opslora!

– Opslora Team
"""

        send_email(
            to_email=data["email"],
            subject=subject,
            body=body
        )

        logger.info(f"Signup email processed for user_id={data['user_id']}")

    except Exception as e:
        logger.error(f"Task failed for payload {payload}: {e}")
        raise