import pytest
from fastapi.testclient import TestClient

from apps.market_api import services
from apps.market_api.exceptions import OrderNotFoundError
from apps.market_api.tests.test_database import override_get_db
from database import get_db
from main import app

client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db


def test_get_order_by_uuid(session, order, create_order, create_user):
    new_user = create_user(session)
    new_order = create_order(session, new_user)

    expected_order = services.get_order_by_uuid(order_uuid=new_order.uuid, db=session)
    assert str(expected_order.uuid) == str(new_order.uuid)

    with pytest.raises(OrderNotFoundError):
        services.get_order_by_uuid(order_uuid=order.uuid, db=session)


def test_get_paginated_products(session):
    expected_product = services.get_paginated_products(db=session)
    assert len(expected_product["data"]) is not None


def test_delete_user_order(session, create_order, create_user):
    new_user = create_user(session)
    new_order = create_order(session, new_user)

    services.delete_user_order(
        user_uuid=new_user.uuid, order_uuid=new_order.uuid, db=session
    )

    with pytest.raises(OrderNotFoundError):
        services.delete_user_order(
            user_uuid=new_user.uuid, order_uuid=new_order.uuid, db=session
        )


def test_update_order_status(session, create_user, create_order):
    new_user = create_user(session)
    new_order = create_order(session, new_user)

    services.update_order_status(
        order_uuid=new_order.uuid, update_status="IN_PROGRESS", db=session
    )
    assert new_order.delivery_status == "IN_PROGRESS"


def test_create_user(session, user):
    expected_user = services.create_user(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        password="1234",
        db=session,
    )

    assert expected_user.email == user.email
