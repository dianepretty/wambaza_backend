import base64
import smtplib
from email.message import EmailMessage
from app.core.config import settings

_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 48 48">
  <rect width="48" height="48" rx="12" fill="#6d28d9"/>
  <g transform="translate(12,11)" fill="none" stroke="#fb923c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6 6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.3.3 0 1 0 .2.3"/>
    <path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/>
    <circle cx="20" cy="10" r="2"/>
  </g>
</svg>"""

_LOGO_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(_LOGO_SVG.encode()).decode()


def _wrap_email(body_html: str) -> str:
    return f"""\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@400;500;600;700&display=swap');
  body, table, td {{
    font-family: 'Josefin Sans', Arial, Helvetica, sans-serif;
  }}
</style>
</head>
<body style="margin:0; padding:0; background:#f5f3ff;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3ff; padding:32px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:20px; overflow:hidden; font-family:'Josefin Sans', Arial, Helvetica, sans-serif;">
          <tr>
            <td style="background:#6d28d9; padding:28px 32px;">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding-right:10px;"><img src="{_LOGO_DATA_URI}" width="36" height="36" alt="Wambaza" style="display:block;" /></td>
                  <td style="font-size:24px; font-weight:700; color:#ffffff; letter-spacing:0.5px;">Wamb<span style="color:#fb923c;">aza</span></td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              {body_html}
            </td>
          </tr>
          <tr>
            <td style="padding:20px 32px; background:#faf9fc; text-align:center;">
              <span style="font-size:12px; color:#9ca3af;">© Wambaza — Safe, private health information</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_temporary_password(to_name: str, to_email: str, temp_password: str):
    signin_url = f"{settings.FRONTEND_URL}/signin"

    msg = EmailMessage()
    msg["Subject"] = "Welcome to Wambaza — your publisher account is ready"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email

    msg.set_content(
        f"Hi {to_name},\n\n"
        f"An admin has created a publisher account for you on Wambaza.\n\n"
        f"Email: {to_email}\n"
        f"Temporary password: {temp_password}\n\n"
        f"Sign in here: {signin_url}\n"
        f"You'll be asked to set a new password on first login.\n\n"
        f"— The Wambaza Team"
    )

    body_html = f"""\
<h2 style="margin:0 0 12px; color:#1f2937; font-size:20px;">Welcome, {to_name} 👋</h2>
<p style="margin:0 0 20px; color:#4b5563; font-size:15px; line-height:1.6;">
  An admin has created a publisher account for you so you can write and publish health articles on Wambaza.
</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3ff; border-radius:12px; margin-bottom:24px;">
  <tr>
    <td style="padding:14px 18px; color:#6b7280; font-size:13px;">Email</td>
    <td style="padding:14px 18px; color:#1f2937; font-size:14px; font-weight:700; text-align:right;">{to_email}</td>
  </tr>
  <tr>
    <td style="padding:14px 18px; color:#6b7280; font-size:13px;">Temporary password</td>
    <td style="padding:14px 18px; color:#1f2937; font-size:14px; font-weight:700; text-align:right;">{temp_password}</td>
  </tr>
</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center">
      <a href="{signin_url}" style="background:#7c3aed; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:999px; font-weight:700; font-size:14px; display:inline-block;">Sign in to Wambaza</a>
    </td>
  </tr>
</table>
<p style="margin:24px 0 0; color:#9ca3af; font-size:13px; text-align:center;">You'll be asked to set a new password the first time you log in.</p>
"""
    msg.add_alternative(_wrap_email(body_html), subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_otp_email(to_name: str, to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Wambaza password reset code"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email

    msg.set_content(
        f"Hi {to_name},\n\n"
        f"Your Wambaza password reset code is: {otp}\n\n"
        f"This code expires in 10 minutes. If you didn't request this, you can ignore this email.\n\n"
        f"— The Wambaza Team"
    )

    body_html = f"""\
<h2 style="margin:0 0 12px; color:#1f2937; font-size:20px;">Reset your password</h2>
<p style="margin:0 0 24px; color:#4b5563; font-size:15px; line-height:1.6;">
  Hi {to_name}, use the code below to reset your Wambaza password. It expires in 10 minutes.
</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3ff; border-radius:12px; margin-bottom:20px;">
  <tr>
    <td align="center" style="padding:24px;">
      <span style="font-size:32px; font-weight:700; color:#6d28d9; letter-spacing:8px;">{otp}</span>
    </td>
  </tr>
</table>
<p style="margin:0; color:#9ca3af; font-size:13px; text-align:center;">Didn't request this? You can safely ignore this email.</p>
"""
    msg.add_alternative(_wrap_email(body_html), subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
