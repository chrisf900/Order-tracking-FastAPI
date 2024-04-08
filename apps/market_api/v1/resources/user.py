from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.auth import utils
from apps.auth.services import get_current_user
from apps.market_api import services
from apps.market_api.exceptions import (
    EmailAlreadyRegisteredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from apps.market_api.responses import (
    APIEmailAlreadyRegisteredError,
    APIUserAlreadyExistsError,
    APIUserNotFoundError,
)
from apps.market_api.schema import AddUserSchema, UpdateUserContactInfoSchema, User
from database import get_db

router = APIRouter(prefix="/market-api/v1")
DBSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/users/{user_uuid}", tags=["Users"], dependencies=[Depends(get_current_user)]
)
def get_user(user_uuid, db: DBSession):
    user = services.get_user_by_uuid(user_uuid=user_uuid, db=db)
    return user


@router.patch(
    "/users/{user_uuid}",
    tags=["Users"],
    response_model=User,
    dependencies=[Depends(get_current_user)],
)
def update_contact_email(
    user_uuid: UUID,
    request_data: UpdateUserContactInfoSchema,
    db: DBSession,
):
    try:
        user = services.update_user_contact_info(
            user_uuid=user_uuid,
            email=request_data.email,
            phone_number=request_data.phone_number,
            db=db,
        )
    except UserNotFoundError:
        return APIUserNotFoundError()
    except EmailAlreadyRegisteredError:
        return APIEmailAlreadyRegisteredError()

    return user


@router.post("/users", response_model=User, tags=["Users"])
def create_user(user: AddUserSchema, db: DBSession):
    try:
        user = services.create_user(
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            email=user.email,
            password=utils.get_password_hash(password=user.password),
            db=db,
        )
    except UserAlreadyExistsError:
        return APIUserAlreadyExistsError()

    return user
