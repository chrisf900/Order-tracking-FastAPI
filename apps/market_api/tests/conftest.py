from datetime import datetime

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from apps.market_api import models
from apps.market_api.schema import OrderSchema, Product, User
from apps.market_api.tests.test_database import override_get_db


class UserFactory(ModelFactory[User]):
    pass


class ProductFactory(ModelFactory[Product]):
    pass


class OrderFactory(ModelFactory[OrderSchema]):
    pass


@pytest.fixture
def user():
    person_instance = UserFactory.build()
    return person_instance


@pytest.fixture
def product():
    product_instance = ProductFactory.build()
    return product_instance


@pytest.fixture
def order():
    order_instance = OrderFactory.build()
    return order_instance


@pytest.fixture
def session(user):
    db = override_get_db()
    session = next(db)
    return session


@pytest.fixture
def create_order():
    def _create_order(db, fake_user):
        new_order = models.Order(user_uuid=fake_user.uuid)
        db.add(new_order)
        db.commit()
        return new_order

    return _create_order


@pytest.fixture
def create_user(user):
    def _create_user(db):
        new_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            email=user.email,
        )
        db.add(new_user)
        db.flush()
        return new_user

    return _create_user


@pytest.fixture
def create_product(user):
    def _create_product(db):
        new_brand = models.Brand(name="brand 1")
        new_category = models.Category(name="Category 1")
        db.add(new_category)
        db.add(new_brand)
        db.flush()
        new_product = models.Product(
            name="Product 1",
            brand_uuid=new_brand.uuid,
            category_uuid=new_category.uuid,
            price=1000.00,
        )
        db.add(new_product)
        db.commit()
        return new_product

    return _create_product


@pytest.fixture
def order_model(order, user):
    user = models.User(
        uuid=user.uuid,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        created_at=datetime.now(),
    )
    return models.Order(
        uuid=order.uuid,
        user_uuid=user.uuid,
        delivery_status="PREPARING_FOR_DELIVERY",
        total_receipt=1000,
        created_at=datetime.now(),
    )
