from fastapi import BackgroundTasks, status
from fastapi.testclient import TestClient

from apps.auth.services import get_current_user, validate_admin_group
from apps.market_api.exceptions import (
    InvalidDeliveryStatusTransition,
    OrderNotFoundError,
)
from apps.market_api.tests.test_database import override_get_db
from database import get_db
from main import app

client = TestClient(app)


async def mock_user():
    return {"user": {"name": "test-user"}}


app.dependency_overrides[get_current_user] = mock_user
app.dependency_overrides[validate_admin_group] = mock_user
app.dependency_overrides[get_db] = override_get_db

FAKE_TOKEN = "Bearer token-123"
URL_PATH = "/market-api/v1/orders/{}"


def test_get_order(mocker, order):
    mock_get_order_by_uuid = mocker.patch(
        "apps.market_api.v1.resources.order.services.get_order_by_uuid",
        return_value=order,
    )
    response = client.get(
        URL_PATH.format(order.uuid), headers={"Authorization": FAKE_TOKEN}
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data["uuid"] == str(order.uuid)

    mock_get_order_by_uuid.side_effect = OrderNotFoundError
    response = client.get(url=URL_PATH.format(order.uuid))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_order_delivery_status(mocker, order_model):
    mock_update_order_status = mocker.patch(
        "apps.market_api.v1.resources.order.services.update_order_status",
        return_value=order_model,
    )
    mocker.patch("apps.market_api.v1.resources.order.services.get_user_by_uuid")
    mocker.patch("apps.market_api.v1.resources.order.send_email")
    mocker.spy(BackgroundTasks, "add_task")

    headers = {"Authorization": FAKE_TOKEN}
    body = {"update_status": "DELIVERED"}

    response = client.post(
        URL_PATH.format(order_model.uuid), headers=headers, json=body
    )
    assert response.status_code == status.HTTP_200_OK

    mock_update_order_status.side_effect = OrderNotFoundError
    response = client.post(
        URL_PATH.format(order_model.uuid), headers=headers, json=body
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    mock_update_order_status.side_effect = InvalidDeliveryStatusTransition
    response = client.post(
        URL_PATH.format(order_model.uuid), headers=headers, json=body
    )
    assert response.status_code == status.HTTP_409_CONFLICT
