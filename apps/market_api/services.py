from uuid import UUID

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.market_api import providers
from apps.market_api.business_logic import DeliveryStateMachine, get_state_class
from apps.market_api.exceptions import (
    CancelOrderIsNotAvailable,
    DeleteProductsIsNotAvailable,
    InvalidDeliveryStatusTransition,
)
from apps.market_api.models import Order, OrderDetail, User
from database import get_db


def get_order_by_uuid(order_uuid: UUID, db: Session = Depends(get_db)) -> Order:
    """
    Get an order by uuid
    :param order_uuid: UUID
    :param db: Session = Depends(get_db)
    :return: Order Model
    """
    order = providers.get_order_by_uuid(order_uuid=order_uuid, db=db)
    return order


def get_paginated_products(
    page_size: int = 10,
    page_num: int = 1,
    db: Session = Depends(get_db),
    search_text: str = None,
) -> dict[str, str]:
    """
    Get paginated products. Search filter by product name
    :param page_size: int = 10
    :param page_num: int = 1
    :param db: Session = Depends(get_db)
    :param search_text: str = None
    :return: dict[str, str]
    """
    products = providers.get_products(db=db, search_text=search_text)
    paginated_products = providers.get_paginated_data_by_query(
        products, page_size, page_num
    )
    return paginated_products


def delete_user_order(
    user_uuid: UUID, order_uuid: UUID, db: Session = Depends(get_db)
) -> None:
    """
    Delete user order (products are also deleted).
    Only products in the status "PREPARING_FOR_DELIVERY" can be deleted
    :param user_uuid: UUID
    :param order_uuid: UUID
    :param db: Session = Depends(get_db)
    :return: None
    """
    order = providers.get_order_by_uuid(order_uuid=order_uuid, db=db)

    if (
        order.user_uuid != user_uuid
        or order.delivery_status != "PREPARING_FOR_DELIVERY"
    ):
        raise CancelOrderIsNotAvailable()

    db.delete(order)
    db.commit()


def get_paginated_user_orders(
    user_uuid: UUID,
    db: Session = Depends(get_db),
    page_size: int = 10,
    page_num: int = 1,
) -> dict[str, str]:
    """
    Get user's orders paginated by user uuid
    :param user_uuid: UUID
    :param db: Session = Depends(get_db)
    :param page_size: int = 10
    :param page_num: int = 1
    :return: dict[str, str]
    """
    user_orders = providers.get_user_orders_by_user_uuid(user_uuid=user_uuid, db=db)
    paginated_user_orders = providers.get_paginated_data_by_query(
        user_orders, page_size, page_num
    )
    return paginated_user_orders


def update_order_status(
    order_uuid: UUID, update_status: str, db: Session = Depends(get_db)
) -> Order:
    """
    Update the user's order based on the status entered.
    There are 3 states handled by a state machine:
    'preparing_for_delivery' | 'in_progress' | 'delivered' | 'cancelled'
    :param order_uuid: UUID
    :param update_status: str
    :param db: Session = Depends(get_db)
    :return: Order Model
    """
    order = providers.get_order_by_uuid(order_uuid=order_uuid, db=db)

    if update_status.upper() == order.delivery_status:
        raise InvalidDeliveryStatusTransition()

    old_state_class = get_state_class(state=order.delivery_status)
    new_state_class = get_state_class(state=update_status.upper())

    dsm = DeliveryStateMachine(state=old_state_class, order=order, db=db)
    dsm.change(new_state_class)

    return order


def create_order_with_products(
    user_uuid: UUID, product_uuids: list[UUID], db: Session = Depends(get_db)
) -> Order:
    """
    Create user order with a list of product uuids
    :param user_uuid: UUID
    :param product_uuids: list[UUID]
    :param db: Session = Depends(get_db)
    :return: Order Model
    """
    order = providers.create_user_order_with_products(
        user_uuid=user_uuid, product_uuids=product_uuids, db=db
    )
    return order


def create_user(
    first_name: str,
    last_name: str,
    phone_number: int,
    email: str,
    password: str,
    db: Session = Depends(get_db),
) -> User:
    """
    Create a new user
    :param first_name: str
    :param last_name: str
    :param phone_number: int
    :param email: str
    :param password: str
    :param db: Session = Depends(get_db)
    :return: User Model
    """
    user = providers.create_user(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        password=password,
        db=db,
    )
    return user


def get_user_by_uuid(user_uuid: UUID, db: Session = Depends(get_db)) -> User:
    """
    Get a user by uuid
    :param user_uuid: UUID
    :param db: Session = Depends(get_db)
    :return: User Model
    """
    user = providers.get_user_by_uuid(user_uuid=user_uuid, db=db)
    return user


def update_user_contact_info(
    user_uuid: UUID,
    db: Session = Depends(get_db),
    email: str = None,
    phone_number: int = None,
) -> User:
    """
    Update the user's contact info. Update email or phone number or both
    :param user_uuid: UUID
    :param email: str = None
    :param phone_number: str = None
    :param db: Session = Depends(get_db)
    :return: User Model
    """
    user = providers.update_user_contact_info(
        user_uuid=user_uuid,
        email=email,
        phone_number=phone_number,
        db=db,
    )
    return user


def get_paginated_products_data_by_order_uuid(
    order_uuid: UUID,
    page_size: int = 10,
    page_num: int = 1,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Get product's orders paginated by order uuid
    :param order_uuid: UUID
    :param page_size: int = 10
    :param page_num: int = 1
    :param db: Session = Depends(get_db)
    :return: dict[str, str]
    """
    products = providers.get_products_data_by_order_uuid(order_uuid=order_uuid, db=db)
    paginated_products = providers.get_paginated_data_by_query(
        products, page_size, page_num
    )
    return paginated_products


def add_order_products(
    order_uuid: UUID, product_uuids: list[UUID], db: Session = Depends(get_db)
) -> None:
    """
    Add products to order
    :param order_uuid: UUID
    :param product_uuids: list[UUID]
    :param db: Session = Depends(get_db)
    :return: None
    """
    order_detail = providers.get_order_products_by_order_uuid(
        order_uuid=order_uuid, db=db
    )
    products = providers.get_products_by_uuids(product_uuids, db=db)

    products_found = {product.uuid for product in products}
    order_products_found = {product.product_uuid for product in order_detail}
    product_uuids = products_found - order_products_found

    bulk_list = []
    for product_uuid in product_uuids:
        bulk_list.append(OrderDetail(order_uuid=order_uuid, product_uuid=product_uuid))

    db.bulk_save_objects(bulk_list)
    db.commit()

    if product_uuids:
        total_receipt = sum(
            [order_product.product.price for order_product in order_detail]
        )
        order = providers.get_order_by_uuid(order_uuid=order_uuid, db=db)
        order.total_receipt = total_receipt
        order.updated_at = func.now()
        db.commit()


def delete_order_products(
    order_uuid: UUID, product_uuids: list[UUID], db: Session = Depends(get_db)
) -> None:
    """
    Delete products from order
    :param order_uuid: UUID
    :param product_uuids: list[UUID]
    :param db: Session = Depends(get_db)
    :return: None
    """
    order = providers.get_order_by_uuid(order_uuid=order_uuid, db=db)

    if order.delivery_status != "PREPARING_FOR_DELIVERY":
        raise DeleteProductsIsNotAvailable()

    providers.delete_order_products(
        order_uuid=order_uuid, product_uuids=product_uuids, db=db
    )

    order_detail = providers.get_order_products_by_order_uuid(
        order_uuid=order_uuid, db=db
    )
    total_receipt = sum([order_product.product.price for order_product in order_detail])

    order.total_receipt = total_receipt
    order.updated_at = func.now()
    db.commit()

    if order_detail.count() == 0:
        order.delete()
        db.commit()
