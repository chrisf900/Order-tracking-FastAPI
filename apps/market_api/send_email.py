import os
from uuid import UUID

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

load_dotenv(".env")


class Settings:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME = os.getenv("MAIN_FROM_NAME")
    TEMPLATE_FOLDER = "apps/market_api/templates"


conf = ConnectionConfig(
    MAIL_USERNAME=Settings.MAIL_USERNAME,
    MAIL_PASSWORD=Settings.MAIL_PASSWORD,
    MAIL_PORT=Settings.MAIL_PORT,
    MAIL_SERVER=Settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM=Settings.MAIL_FROM,
    MAIL_FROM_NAME=Settings.MAIL_FROM_NAME,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Settings.TEMPLATE_FOLDER,
)


async def send_email(
    email_to: str, order_uuid: UUID, username: str, delivery_status: str
) -> None:
    subject = "[FastAPI_Testing] New Order Status Update"
    body = {
        "order_uuid": order_uuid,
        "username": username,
        "order_status": delivery_status,
    }

    msg = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(config=conf)
    await fm.send_message(message=msg, template_name="email.html")
