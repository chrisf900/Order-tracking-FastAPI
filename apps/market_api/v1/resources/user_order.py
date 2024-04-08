from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from apps.auth.services import get_current_user
from apps.market_api import services
from apps.market_api.exceptions import CancelOrderIsNotAvailable, OrderNotFoundError
from apps.market_api.responses import (
    APICancelOrderIsNotAvailableError,
    APIOrderDoesNotExistError,
)
from apps.market_api.schema import CreateOrderSchema, OrderSchema, PaginatedResponse
from database import get_db

router = APIRouter(prefix="/market-api/v1", dependencies=[Depends(get_current_user)])
DBSession = Annotated[Session, Depends(get_db)]


@router.post("/users/{user_uuid}/orders/", tags=["User Orders"])
def create_user_order(user_uuid: UUID, request_data: CreateOrderSchema, db: DBSession):
    order = services.create_order_with_products(
        user_uuid=user_uuid, product_uuids=request_data.product_uuids, db=db
    )
    return order


@router.get(
    "/users/{user_uuid}/orders",
    response_model=PaginatedResponse[OrderSchema],
    tags=["User Orders"],
)
def get_user_orders(
    user_uuid: UUID,
    db: DBSession,
    page: Annotated[int, Query(ge=1)] = 1,
):
    user_orders = services.get_paginated_user_orders(
        user_uuid=user_uuid, page_num=page, db=db
    )
    return user_orders


@router.delete(
    "/users/{user_uuid}/orders/{order_uuid}",
    tags=["User Orders"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_order(user_uuid: UUID, order_uuid: UUID, db: DBSession):
    try:
        services.delete_user_order(user_uuid=user_uuid, order_uuid=order_uuid, db=db)
    except OrderNotFoundError:
        return APIOrderDoesNotExistError()
    except CancelOrderIsNotAvailable:
        return APICancelOrderIsNotAvailableError()
