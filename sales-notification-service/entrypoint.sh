#!/bin/sh

echo "Waiting for RabbitMQ..."

until nc -z rabbitmq 5672
do
  echo "RabbitMQ not ready..."
  sleep 2
done

echo "RabbitMQ is ready!"
echo "Starting Celery worker..."

celery -A app.core.celery_app worker \
  --loglevel=info \
  -Q notification_queue