from fastapi import status
from fastapi.testclient import TestClient

from apps.auth.services import get_current_user
from apps.market_api.exceptions import DeleteProductsIsNotAvailable, OrderNotFoundError
from main import app

client = TestClient(app)


async def mock_user():
    return {"user": {"name": "test-user"}}


app.dependency_overrides[get_current_user] = mock_user

FAKE_TOKEN = "Bearer token-123"
URL_PATH = "/market-api/v1/orders/{}/products"


def test_get_order_products(mocker, order, product):
    mocker.patch(
        "apps.market_api.v1.resources.order_product.services.get_paginated_products_data_by_order_uuid",
        return_value={"count": 1, "data": [product]},
    )
    response = client.get(
        URL_PATH.format(order.uuid), headers={"Authorization": FAKE_TOKEN}
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["data"]) == 1


def test_add_order_products(mocker, order):
    mock_update_order_status = mocker.patch(
        "apps.market_api.v1.resources.order.services.add_order_products"
    )
    headers = {"Authorization": FAKE_TOKEN}
    body = {
        "product_uuids": [
            "0277436f-213d-47f3-8e8d-e22343b0fee3",
            "3aeaf80d-067d-459d-ba94-2819ed3c8d76",
        ]
    }

    response = client.post(
        f"/market-api/v1/orders/{order.uuid}/products/", headers=headers, json=body
    )
    assert response.status_code == status.HTTP_201_CREATED

    mock_update_order_status.side_effect = OrderNotFoundError
    response = client.post(
        f"/market-api/v1/orders/{order.uuid}/products/", headers=headers, json=body
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_order_products(mocker, order):
    mock_update_order_status = mocker.patch(
        "apps.market_api.v1.resources.order.services.delete_order_products"
    )
    headers = {"Authorization": FAKE_TOKEN}

    response = client.delete(
        url=URL_PATH.format(order.uuid)
        + "?product_uuids=3fa85f64-5717-4562-b3fc-2c963f66afa6",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK

    mock_update_order_status.side_effect = OrderNotFoundError
    response = client.delete(
        url=URL_PATH.format(order.uuid)
        + "?product_uuids=3fa85f64-5717-4562-b3fc-2c963f66afa6",
        headers=headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    mock_update_order_status.side_effect = DeleteProductsIsNotAvailable
    response = client.delete(
        url=URL_PATH.format(order.uuid)
        + "?product_uuids=3fa85f64-5717-4562-b3fc-2c963f66afa6",
        headers=headers,
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
