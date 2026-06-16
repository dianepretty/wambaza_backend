import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_temporary_password(to_email: str, temp_password: str):
    msg = EmailMessage()
    msg["Subject"] = "Wambaza: Your temporary password"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(f"Your temporary password is: {temp_password}\nPlease change it after first login.")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
