from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(email: EmailStr, username: str, host: str, token: str):
    message = MessageSchema(
        subject="Confirm your email",
        recipients=[email],
        body=f"""
        <p>Hi {username},</p>
        <p>Thanks for using our application! Please confirm your email address by clicking the link below:</p>
        <p><a href="{host}api/auth/confirmed_email/{token}">Confirm Email</a></p>
        <p>If you did not sign up for this account, please ignore this email.</p>
        """,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
