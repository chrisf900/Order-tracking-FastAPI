import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "user"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("group.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )

    order = relationship("Order", back_populates="user", cascade="all, delete")
    group = relationship("Group", back_populates="user")


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)

    user = relationship("User", back_populates="group")


class PasswordHistory(Base):
    __tablename__ = "password_history"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    user_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.uuid"))
    password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User")


class Product(Base):
    __tablename__ = "product"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    brand_uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brand.uuid")
    )
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    unit: Mapped[float] = mapped_column(Float, nullable=True)
    unit_size: Mapped[float] = mapped_column(Float, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=True)
    category_uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.uuid")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )

    brand = relationship("Brand")
    category = relationship("Category")


class Brand(Base):
    __tablename__ = "brand"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )


class Category(Base):
    __tablename__ = "category"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )


class Order(Base):
    __tablename__ = "order"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    user_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.uuid"))
    delivery_status: Mapped[str] = mapped_column(
        String(30), default="PREPARING_FOR_DELIVERY", index=True
    )
    total_receipt: Mapped[float] = mapped_column(Float, nullable=True, default=float(0))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )

    user = relationship("User", back_populates="order")
    order_detail = relationship(
        "OrderDetail", back_populates="order", cascade="all, delete"
    )


class OrderDetail(Base):
    __tablename__ = "order_detail"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    order_uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order.uuid")
    )
    product_uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product.uuid")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )

    order = relationship("Order", cascade="all, delete")
    product = relationship("Product")
