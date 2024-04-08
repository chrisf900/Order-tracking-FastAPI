from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from apps.auth.services import get_current_user
from apps.market_api import services
from apps.market_api.exceptions import DeleteProductsIsNotAvailable, OrderNotFoundError
from apps.market_api.responses import (
    APIDeleteProductsIsNotAvailableError,
    APIOrderDoesNotExistError,
)
from apps.market_api.schema import AddOrderProductsSchema, PaginatedResponse, Product
from database import get_db

router = APIRouter(prefix="/market-api/v1", dependencies=[Depends(get_current_user)])
DBSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/orders/{order_uuid}/products",
    response_model=PaginatedResponse[Product],
    tags=["Order Products"],
)
def get_order_products(
    order_uuid: UUID,
    db: DBSession,
    page: Annotated[int, Query(ge=1)] = 1,
):
    order_products = services.get_paginated_products_data_by_order_uuid(
        order_uuid=order_uuid, page_num=page, db=db
    )
    return order_products


@router.post(
    "/orders/{order_uuid}/products/",
    tags=["Order Products"],
    status_code=status.HTTP_201_CREATED,
)
def add_order_products(
    order_uuid: UUID,
    request_data: AddOrderProductsSchema,
    db: DBSession,
):
    try:
        services.add_order_products(
            order_uuid=order_uuid, product_uuids=request_data.product_uuids, db=db
        )
    except OrderNotFoundError:
        return APIOrderDoesNotExistError()


@router.delete("/orders/{order_uuid}/products", tags=["Order Products"])
def delete_order_products(
    order_uuid: UUID,
    db: DBSession,
    product_uuids: list[UUID] = Query(None),
):
    try:
        services.delete_order_products(
            order_uuid=order_uuid, product_uuids=product_uuids, db=db
        )
    except OrderNotFoundError:
        return APIOrderDoesNotExistError()
    except DeleteProductsIsNotAvailable:
        return APIDeleteProductsIsNotAvailableError()
