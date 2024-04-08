import json
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from apps.auth import utils
from apps.market_api.models import (
    Brand,
    Category,
    Group,
    PasswordHistory,
    Product,
    User,
)
from database import get_db


def read_data():
    with open("dummydata.json") as f:
        data = json.load(f)
        products = data["products"]
        admin_users = data["users"]

    return products, admin_users


def create_data():
    s = next(get_db())
    products, users = read_data()
    categories = {product["category"] for product in products}

    # set user groups, product categories, product brands
    groups = [Group(name="admin"), Group(name="customer")]
    categories = [
        Category(name=category, created_at=datetime.now()) for category in categories
    ]
    brands = [
        Brand(name=product["brand"], created_at=datetime.now()) for product in products
    ]

    s.bulk_save_objects(groups)
    s.bulk_save_objects(categories)
    s.bulk_save_objects(brands)

    admin = s.query(Group).filter(Group.name == "admin").first().id

    # set users
    for user in users:
        u = User(
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            phone_number=user["phone_number"],
            group_id=admin,
        )
        s.add(u)
        s.flush()

        password_history = PasswordHistory(
            user_uuid=u.uuid,
            password=utils.get_password_hash(password=user["password"]),
        )
        s.add(password_history)

    print("Admin User Created -> admin@admin.com:admin")

    # set products
    p = []
    brand_qry = s.query(Brand).all()
    category_qry = s.query(Category).all()
    brand_uuids = {brand.name: brand.uuid for brand in brand_qry}
    category_uuids = {category.name: category.uuid for category in category_qry}

    for product in products:
        p.append(
            Product(
                name=product["name"],
                sku=product["sku"],
                brand_uuid=brand_uuids.get(product["brand"]),
                description=product["description"],
                unit=product["unit"],
                unit_size=product["unit_size"],
                weight=product["weight"],
                price=product["price"],
                category_uuid=category_uuids.get(product["category"]),
                created_at=datetime.now(),
            )
        )

    s.bulk_save_objects(p)
    s.commit()
    print("[OK] Data Created")


try:
    create_data()
except IntegrityError as e:
    print("[FAIL] ERROR:", e)
