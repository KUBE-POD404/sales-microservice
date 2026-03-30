import logging
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.exceptions.custom_exceptions import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


def create_customer_service(
    db: Session,
    name: str,
    email: str,
    organization_id: int,
    created_by_user_id: int
) -> Customer:

    logger.info("Creating customer", extra={"email": email})

    customer = Customer(
        organization_id=organization_id,
        name=name,
        email=email,
        created_by_user_id=created_by_user_id,
        created_at=datetime.now(timezone.utc),
    )

    db.add(customer)

    try:
        db.commit()
        db.refresh(customer)
        logger.info("Customer created", extra={"customer_id": customer.id})
        return customer
    except IntegrityError:
        db.rollback()
        logger.warning("Customer email conflict", extra={"email": email})
        raise ConflictException("Customer email already exists")


def get_customer(db: Session, customer_id: int, organization_id: int) -> Customer:

    logger.info("Fetching customer", extra={"customer_id": customer_id})

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.organization_id == organization_id
        )
        .first()
    )

    if not customer:
        logger.warning("Customer not found", extra={"customer_id": customer_id})
        raise NotFoundException("Customer not found")

    return customer


def list_customers_service(
    db: Session,
    organization_id: int,
    offset: int = 0,
    limit: int = 15
):
    logger.info("Listing customers", extra={"offset": offset, "limit": limit})

    return (
        db.query(Customer)
        .filter(Customer.organization_id == organization_id)
        .order_by(Customer.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_customer(
    db: Session,
    customer_id: int,
    organization_id: int,
    name: str,
    email: str
):
    logger.info("Updating customer", extra={"customer_id": customer_id})

    customer = get_customer(db, customer_id, organization_id)

    customer.name = name
    customer.email = email

    try:
        db.commit()
        db.refresh(customer)
        logger.info("Customer updated", extra={"customer_id": customer.id})
        return customer
    except IntegrityError:
        db.rollback()
        logger.warning("Email conflict on update", extra={"email": email})
        raise ConflictException("Email already exists")


def customer_exists(
    db: Session,
    customer_id: int,
    organization_id: int
) -> bool:

    logger.info("Checking customer existence", extra={"customer_id": customer_id})

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.organization_id == organization_id
        )
        .first()
    )

    return customer is not None