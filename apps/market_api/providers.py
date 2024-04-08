from typing import List
from uuid import UUID

from fastapi import Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.market_api.exceptions import (
    EmailAlreadyRegisteredError,
    OrderNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from apps.market_api.models import Order, OrderDetail, PasswordHistory, Product, User


def get_order_by_uuid(order_uuid: UUID, db: Session):
    order = db.query(Order).filter(Order.uuid == order_uuid).first()

    if not order:
        raise OrderNotFoundError(order_uuid)

    return order


def get_order_products_by_order_uuid(order_uuid: UUID, db: Session):
    order_products = db.query(OrderDetail).filter(OrderDetail.order_uuid == order_uuid)
    return order_products


def get_products_data_by_order_uuid(order_uuid: UUID, db: Session):
    order_products = db.query(OrderDetail).filter(OrderDetail.order_uuid == order_uuid)
    product_uuids = {product.product_uuid for product in order_products}
    products = db.query(Product).filter(Product.uuid.in_(product_uuids))

    return products


def get_paginated_data_by_query(
    query: Query,
    page_size: int = 10,
    page_num: int = 1,
):
    data = [p for p in query.limit(page_size).offset(page_num - 1)]
    return {
        "count": len(data),
        "data": data,
    }


def update_user_contact_info(
    user_uuid: UUID, db: Session, email: str = None, phone_number: int = None
):
    try:
        user = db.query(User).filter(User.uuid == user_uuid).first()

        if not user:
            raise UserNotFoundError(user_uuid)

        if email:
            user.email = email

        if phone_number:
            user.phone_number = phone_number

        user.updated_at = func.now()
        db.commit()
    except IntegrityError:
        raise EmailAlreadyRegisteredError()

    return user


def create_user(
    first_name: str,
    last_name: str,
    phone_number: int,
    email: str,
    password: str,
    db: Session,
):
    try:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
        )
        db.add(user)
        db.flush()

        password_history = PasswordHistory(user_uuid=user.uuid, password=password)
        db.add(password_history)

        db.commit()
    except IntegrityError:
        raise UserAlreadyExistsError()

    return user


def get_user_by_uuid(user_uuid: UUID, db: Session):
    user = db.query(User).filter(User.uuid == user_uuid).first()

    if not user:
        raise UserNotFoundError(user_uuid)
    return user


def get_products(db: Session, search_text: str = None):
    products = db.query(Product)

    if search_text:
        products = db.query(Product).filter(Product.name.ilike(f"%{search_text}%"))
    return products


def get_user_orders_by_user_uuid(user_uuid: UUID, db: Session):
    user_orders = db.query(Order).filter(Order.user_uuid == user_uuid)
    return user_orders


def create_user_order_with_products(
    user_uuid: UUID, product_uuids: List[UUID], db: Session
):
    products = db.query(Product).filter(Product.uuid.in_(product_uuids))
    product_uuids_list = [product.uuid for product in products]
    total_receipt = sum([product.price for product in products])

    order = Order(user_uuid=user_uuid, total_receipt=total_receipt)
    db.add(order)
    db.flush()

    bulk_list = []
    for product_uuid in product_uuids_list:
        bulk_list.append(OrderDetail(order_uuid=order.uuid, product_uuid=product_uuid))

    db.bulk_save_objects(bulk_list)
    db.commit()

    return order


def get_products_by_uuids(product_uuids: list[UUID], db: Session):
    products = db.query(Product).filter(Product.uuid.in_(product_uuids))
    return products


def delete_order_products(order_uuid: UUID, product_uuids: list[UUID], db: Session):
    order_detail = (
        db.query(OrderDetail)
        .filter(OrderDetail.order_uuid == order_uuid)
        .filter(OrderDetail.product_uuid.in_(product_uuids))
    )
    db.delete(order_detail)
    db.commit()

    return order_detail
