"""Email sending service using Gmail SMTP."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

def _get_smtp_credentials():
    """Retrieve generic SMTP credentials from application settings."""
    username = settings.smtp_username or settings.smtp_email or settings.gmail_email
    password = settings.smtp_password or settings.gmail_app_password
    sender = settings.smtp_sender_email or settings.smtp_email or settings.gmail_email or username
    return settings.smtp_host, settings.smtp_port, username, password, sender


async def send_email(to: str, subject: str, html_body: str, reply_to: str | None = None) -> bool:
    """
    Send an HTML email via Gmail SMTP.

    Supports Brevo, Gmail, or any STARTTLS-compatible SMTP relay.
    """
    smtp_host, smtp_port, smtp_username, smtp_password, sender_email = _get_smtp_credentials()
    if not smtp_username or not smtp_password or not sender_email:
        logger.warning("SMTP credentials or sender not set — email not sent")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        # Use synchronous SMTP in a thread-safe way (FastAPI runs async but
        # smtplib is blocking; for low volume this is fine)
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, to, msg.as_string())

        logger.info(f"Email sent to {to}", extra={"subject": subject})
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def _build_contact_email_html(data: dict) -> str:
    """Build a nice HTML email for a contact form submission."""
    return f"""
    <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #7c3aed;">📩 Nouveau message de contact</h2>
        <table style="border-collapse: collapse; width: 100%; margin-top: 16px;">
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold; width: 120px;">Nom</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{data.get('first_name', '')} {data.get('last_name', '')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Téléphone</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{data.get('phone', '')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Email</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><a href="mailto:{data.get('email', '')}">{data.get('email', '')}</a></td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Sujet</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{data.get('subject', '')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; font-weight: bold; vertical-align: top;">Message</td>
                <td style="padding: 8px 0;">{data.get('message', '').replace(chr(10), '<br>')}</td>
            </tr>
        </table>
        <p style="color: #999; font-size: 12px; margin-top: 24px;">— Envoyé depuis le site Église LaRencontre</p>
    </div>
    """


def _build_reservation_email_html(data: dict) -> str:
    """Build a nice HTML email for a boutique reservation."""
    product = data.get("product", {})
    return f"""
    <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #7c3aed;">🛍️ Nouvelle réservation boutique</h2>
        <table style="border-collapse: collapse; width: 100%; margin-top: 16px;">
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold; width: 140px;">Client</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{data.get('name', '')} {data.get('firstname', '')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Téléphone</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><a href="tel:{data.get('phone', '')}">{data.get('phone', '')}</a></td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Produit</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{product.get('name', '')} ({product.get('category', '')})</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Taille</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{data.get('size', '-')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee; font-weight: bold;">Couleur</td>
                <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{data.get('color', '-')}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; font-weight: bold;">Quantité</td>
                <td style="padding: 8px 0;">{data.get('quantity', 1)}</td>
            </tr>
        </table>
        <p style="color: #999; font-size: 12px; margin-top: 24px;">— Réservation depuis le site Église LaRencontre</p>
    </div>
    """
