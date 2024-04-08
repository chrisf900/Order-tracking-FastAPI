from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from apps.auth.responses import APIIncorrectUserOrPasswordError
from apps.auth.schema import Token
from apps.auth.utils import authenticate_user, create_access_token
from database import get_db

router = APIRouter()


@router.post("/api/v1/login", response_model=Token, tags=["Auth"])
def login_for_access_token(
    user_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(
        username=user_details.username, password=user_details.password, db=db
    )
    if not user:
        raise APIIncorrectUserOrPasswordError

    access_token = create_access_token(data={"sub": str(user.uuid)})

    return Token(access_token=access_token, token_type="bearer")
