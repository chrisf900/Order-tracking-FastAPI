from fastapi import status
from fastapi.testclient import TestClient

from apps.auth.services import get_current_user
from apps.market_api.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    EmailAlreadyRegisteredError,
)
from main import app

client = TestClient(app)


async def mock_user():
    return {"user": {"name": "test-user"}}


app.dependency_overrides[get_current_user] = mock_user

FAKE_TOKEN = "Bearer token-123"
PATH_URL = "/market-api/v1/users/{}"


def test_get_user(mocker, user):
    mocker.patch(
        "apps.market_api.v1.resources.user.services.get_user_by_uuid", return_value=user
    )
    response = client.get(
        PATH_URL.format(user.uuid), headers={"Authorization": FAKE_TOKEN}
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data["uuid"] == str(user.uuid)


def test_update_contact_email(mocker, user):
    mock_update_user_contact_info = mocker.patch(
        "apps.market_api.v1.resources.user.services.update_user_contact_info",
        return_value=user,
    )
    headers = {"Authorization": FAKE_TOKEN}
    body = {"email": user.email, "phone_number": user.phone_number}

    response = client.patch(PATH_URL.format(user.uuid), headers=headers, json=body)
    assert response.status_code == status.HTTP_200_OK

    mock_update_user_contact_info.side_effect = UserNotFoundError
    response = client.patch(PATH_URL.format(user.uuid), headers=headers, json=body)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    mock_update_user_contact_info.side_effect = EmailAlreadyRegisteredError
    response = client.patch(PATH_URL.format(user.uuid), headers=headers, json=body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user(mocker, user):
    mock_create_user = mocker.patch(
        "apps.market_api.v1.resources.user.services.create_user", return_value=user
    )
    headers = {"Authorization": FAKE_TOKEN}
    body = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "email": user.email,
        "password": "1234",
    }

    response = client.post(
        url="/market-api/v1/users",
        headers=headers,
        json=body,
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["uuid"] == str(user.uuid)

    mock_create_user.side_effect = UserAlreadyExistsError
    response = client.post("/market-api/v1/users", headers=headers, json=body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
