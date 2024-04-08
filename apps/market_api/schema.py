from datetime import datetime
from typing import Generic, List, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

M = TypeVar("M")


class User(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    phone_number: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime | None = None
    group_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class Brand(BaseModel):
    uuid: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    uuid: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    uuid: UUID
    name: str
    sku: str | None = None
    brand: Brand | None = None
    description: str | None = None
    unit: float | None = None
    unit_size: float | None = None
    weight: float | None = None
    price: float | None = None
    category: Category | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    uuid: UUID
    user_uuid: UUID
    delivery_status: str
    total_receipt: float
    created_at: datetime
    updated_at: datetime = None

    model_config = ConfigDict(from_attributes=True)


class OrderDetail(BaseModel):
    uuid: UUID
    order_uuid: UUID
    quantity: int
    created_at: datetime
    updated_at: datetime | None = None
    products: list[Product] = []

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    uuid: UUID
    user: User
    delivery_status: str
    total_receipt: float
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StatusSchema(BaseModel):
    update_status: str

    @field_validator("update_status")
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        states = ["IN_PROGRESS", "DELIVERED", "CANCELLED"]
        if v.upper() not in states:
            raise ValueError("Invalid state name")
        return v.title()


class AddOrderProductsSchema(BaseModel):
    product_uuids: list[UUID]


class CreateOrderSchema(BaseModel):
    product_uuids: list[UUID]


class AddUserSchema(BaseModel):
    first_name: str
    last_name: str
    phone_number: int
    email: EmailStr
    password: str


class UpdateUserContactInfoSchema(BaseModel):
    email: EmailStr | None = None
    phone_number: int | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values):
        if not values:
            raise ValueError("email field or phone_number field is required")
        return values


class PaginatedResponse(BaseModel, Generic[M]):
    count: int
    data: List[M]
