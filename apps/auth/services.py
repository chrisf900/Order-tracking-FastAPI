from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from apps.auth.responses import APICredentialError, APIUserPermissionsError
from apps.auth.utils import verify_token_access
from apps.market_api import models
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login", scheme_name="JWT")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> models.User:
    token_data = verify_token_access(token=token)
    user = (
        db.query(models.User).filter(models.User.uuid == token_data.user_uuid).first()
    )

    if user is None:
        raise APICredentialError

    return user


def validate_admin_group(
    user: Annotated[models.User, Depends(get_current_user)]
) -> bool:
    user_group = user.group

    if user_group and user_group.name in ["admin"]:
        return True

    raise APIUserPermissionsError
