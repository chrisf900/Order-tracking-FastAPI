from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from apps.auth.services import get_current_user, validate_admin_group
from apps.market_api import services
from apps.market_api.exceptions import (
    InvalidDeliveryStatusTransition,
    OrderNotFoundError,
)
from apps.market_api.responses import (
    APIInvalidDeliveryStatusTransition,
    APIOrderDoesNotExistError,
)
from apps.market_api.schema import OrderSchema, StatusSchema
from apps.market_api.send_email import send_email
from database import get_db

router = APIRouter(prefix="/market-api/v1", dependencies=[Depends(get_current_user)])
DBSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/orders/{order_uuid}",
    tags=["Orders"],
    response_model=OrderSchema,
)
def get_order(order_uuid: UUID, db: DBSession):
    try:
        order = services.get_order_by_uuid(order_uuid=order_uuid, db=db)
    except OrderNotFoundError:
        return APIOrderDoesNotExistError()

    return order


@router.post(
    "/orders/{order_uuid}",
    tags=["Orders"],
    dependencies=[Depends(validate_admin_group)],
)
def update_order_delivery_status(
    order_uuid: UUID,
    request_data: StatusSchema,
    db: DBSession,
    background_tasks: BackgroundTasks,
):
    try:
        order = services.update_order_status(
            order_uuid=order_uuid, update_status=request_data.update_status, db=db
        )
        user = services.get_user_by_uuid(user_uuid=order.user_uuid, db=db)

        background_tasks.add_task(
            send_email,
            email_to=user.email,
            order_uuid=order.uuid,
            username=user.first_name,
            delivery_status=order.delivery_status,
        )
    except OrderNotFoundError:
        return APIOrderDoesNotExistError()
    except InvalidDeliveryStatusTransition:
        return APIInvalidDeliveryStatusTransition()

    return order


'''
from fastapi_sqlalchemy import db
from apps.market_api.models import Brand, Category, Product
from datetime import datetime

# db_user = User(first_name="Pepe", last_name="Lazo", phone_number=999999999, email="pepe@lazo.com")
# db_user = Order(user_uuid="3aeaf80d-067d-459d-ba94-2819ed3c8d76", delivery_status="PREPARING_FOR_DELIVERY")
db_product = Product(
    name="Product 1",
    sku="123",
    brand_uuid=UUID(int=1),
    description="Product 1 description",
    unit=1,
    unit_size=1,
    weight=400,
    price=3000,
    category_uuid=UUID(int=1),
    created_at=datetime.now()
)


users = [
    User(name='John', email='john@example.com'),
    User(name='Alice', email='alice@example.com')
]
profiles = [
    Profile(bio='Bio for John', user=users[0]),
    Profile(bio='Bio for Alice', user=users[1])
]
session.add_all(users)
session.add_all(profiles)
session.commit()

'''
