"""Contact API endpoints — saves to Google Sheet and sends email notification."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from app.models.contact import ContactSubmission, ContactResponse
from app.services.sheets_write_service import append_row
from app.services.email_service import send_email
from app.services.email_templates import build_contact_email
from app.services import sheets_service
from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter()

# Subject labels for readability
_SUBJECT_LABELS = {
    "general": "Question générale",
    "home-group": "Home Groups",
    "baptism": "Baptême",
    "prayer": "Demande de prière",
    "other": "Autre",
}

_SUBJECT_CATEGORIES = {
    "general": "general",
    "home-group": "home_group",
    "baptism": "baptism",
    "prayer": "prayer_request",
    "other": "other",
}


@router.post("", response_model=ContactResponse, status_code=201)
async def submit_contact(data: ContactSubmission, request: Request):
    """
    Handle a contact form submission:
      1. Save to the Google Sheet (SHEET_ID_CONTACT)
      2. Send notification email to the church email
    """
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    ip_address = forwarded_for or (request.client.host if request.client else "")
    subject_label = _SUBJECT_LABELS.get(data.subject, data.subject)

    # --- 1. Write to Google Sheet ---
    sheet_id = settings.sheet_id_contact
    row = [
        "=ROW()-1",
        data.first_name,
        data.last_name,
        data.email,
        data.phone,
        subject_label,
        data.message,
        _SUBJECT_CATEGORIES.get(data.subject, data.subject),
        "pending",
        "",
        "",
        "",
        ip_address,
        created_at,
    ]
    written = await append_row(sheet_id, settings.sheet_name_contact, row)
    if not written:
        logger.error("Could not write contact to Google Sheet")
        raise HTTPException(
            status_code=503,
            detail="Le message n’a pas pu être enregistré. Veuillez réessayer.",
        )

    # --- 2. Send email notification ---
    recipients = await sheets_service.get_notification_recipients()

    full_name = f"{data.first_name} {data.last_name}".strip()
    subject = f"📩 Nouveau contact : {subject_label} — {full_name}"
    html = build_contact_email(data.model_dump(), subject_label)

    # L'enregistrement Sheets reste la source de vérité. Une panne SMTP ne doit
    # pas inciter l'utilisateur à renvoyer le formulaire et créer un doublon.
    email_results = [
        await send_email(to=recipient, subject=subject, html_body=html, reply_to=data.email)
        for recipient in recipients
    ]
    if not all(email_results):
        logger.warning("One or more contact notification emails could not be sent", extra={
            "recipient_count": len(recipients),
            "failed_count": email_results.count(False),
        })

    logger.info(f"Contact submission from {full_name} ({data.email})", extra={"subject": data.subject})
    return ContactResponse()
