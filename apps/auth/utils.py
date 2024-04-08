import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from apps.auth.responses import APICredentialError
from apps.auth.schema import TokenData
from apps.market_api import models
from apps.market_api.models import User
from database import get_db

load_dotenv(".env")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login", scheme_name="JWT")

SECRET_KEY = os.environ["OAUTH2_SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def verify_password(non_hashed_pass, hashed_pass) -> bool:
    return bcrypt.checkpw(non_hashed_pass.encode(), hashed_pass.encode())


def authenticate_user(
    username: str, password: str, db: Session = Depends(get_db)
) -> bool | User:
    user = db.query(models.User).filter(models.User.email == username).first()

    if not user:
        return False

    user_pw = (
        db.query(models.PasswordHistory)
        .filter(models.PasswordHistory.user_uuid == user.uuid)
        .first()
    )

    if not user_pw:
        return False

    if not verify_password(password, user_pw.password):
        return False
    return user


def verify_token_access(token: str) -> TokenData:
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        user_uuid: str = payload.get("sub")

        if user_uuid is None:
            raise APICredentialError

        token_data = TokenData(user_uuid=user_uuid)
    except JWTError:
        raise APICredentialError

    return token_data


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
