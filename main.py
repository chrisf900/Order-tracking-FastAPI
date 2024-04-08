import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from apps.auth import auth
from apps.market_api.v1.resources import product, user_order
from apps.market_api.v1.resources import order_product, user, order

load_dotenv(".env")

app = FastAPI()


app.include_router(auth.router)
app.include_router(order.router)
app.include_router(order_product.router)
app.include_router(product.router)
app.include_router(user.router)
app.include_router(user_order.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
