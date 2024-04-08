from fastapi import status
from fastapi.testclient import TestClient

from apps.auth.services import get_current_user
from main import app

client = TestClient(app)


async def mock_user():
    return {"user": {"name": "test-user"}}


app.dependency_overrides[get_current_user] = mock_user

FAKE_TOKEN = "Bearer token-123"
URL_PATH = "/market-api/v1/products"


def test_get_products(mocker, product):
    mocker.patch(
        "apps.market_api.v1.resources.order_product.services.get_paginated_products",
        return_value={"count": 1, "data": [product]},
    )
    response = client.get(URL_PATH, headers={"Authorization": FAKE_TOKEN})
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["data"]) == 1
