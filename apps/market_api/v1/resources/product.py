from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.auth.services import get_current_user
from apps.market_api import services
from apps.market_api.schema import PaginatedResponse, Product
from database import get_db

router = APIRouter(prefix="/market-api/v1", dependencies=[Depends(get_current_user)])
DBSession = Annotated[Session, Depends(get_db)]


@router.get("/products", response_model=PaginatedResponse[Product], tags=["Products"])
def get_products(
    db: DBSession,
    page: Annotated[int, Query(ge=1)] = 1,
    name: str = Query(None),
):
    products = services.get_paginated_products(page_num=page, search_text=name, db=db)
    return products
