from celery import Celery
import os

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@rabbitmq:5672//"
)

celery = Celery(
    "auth_service",
    broker=RABBITMQ_URL,
    backend="rpc://"
)

celery.conf.update(
    task_routes={
        "notification.send_signup_email": {"queue": "notification_queue"}
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)