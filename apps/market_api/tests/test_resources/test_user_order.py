from fastapi import status
from fastapi.testclient import TestClient

from apps.auth.services import get_current_user
from apps.market_api.exceptions import CancelOrderIsNotAvailable, OrderNotFoundError
from main import app

client = TestClient(app)


async def mock_user():
    return {"user": {"name": "test-user"}}


app.dependency_overrides[get_current_user] = mock_user

FAKE_TOKEN = "Bearer token-123"


def test_create_user_order(mocker, user, order):
    mocker.patch(
        "apps.market_api.v1.resources.order.services.create_order_with_products"
    )
    headers = {"Authorization": FAKE_TOKEN}
    body = {
        "product_uuids": [
            "3aeaf80d-067d-459d-ba94-2819ed3c8d76",
            "0277436f-213d-47f3-8e8d-e22343b0fee3",
        ]
    }

    response = client.post(
        url=f"/market-api/v1/users/{user.uuid}/orders/",
        headers=headers,
        json=body,
    )
    assert response.status_code == status.HTTP_200_OK


def test_get_user_orders(mocker, user, order):
    mocker.patch(
        "apps.market_api.v1.resources.order.services.get_paginated_user_orders",
        return_value={"count": 1, "data": [order]},
    )
    headers = {"Authorization": FAKE_TOKEN}

    response = client.get(f"/market-api/v1/users/{user.uuid}/orders", headers=headers)
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["data"]) == 1


def test_delete_user_order(mocker, user, order):
    mock_delete_user_order = mocker.patch(
        "apps.market_api.v1.resources.order.services.delete_user_order"
    )
    headers = {"Authorization": FAKE_TOKEN}

    response = client.delete(
        url=f"/market-api/v1/users/{user.uuid}/orders/{order.uuid}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    mock_delete_user_order.side_effect = OrderNotFoundError
    response = client.delete(
        url=f"/market-api/v1/users/{user.uuid}/orders/{order.uuid}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    mock_delete_user_order.side_effect = CancelOrderIsNotAvailable
    response = client.delete(
        url=f"/market-api/v1/users/{user.uuid}/orders/{order.uuid}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
