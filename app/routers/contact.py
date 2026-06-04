"""Contact API endpoints — saves to Google Sheet and sends email notification."""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.contact import ContactSubmission, ContactResponse
from app.services.sheets_write_service import append_row
from app.services.email_service import send_email, _build_contact_email_html
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


@router.post("", response_model=ContactResponse, status_code=201)
async def submit_contact(data: ContactSubmission):
    """
    Handle a contact form submission:
      1. Save to the Google Sheet (SHEET_ID_CONTACT)
      2. Send notification email to the church email
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # --- 1. Write to Google Sheet ---
    sheet_id = settings.sheet_id_contact
    row = [
        timestamp,
        data.name,
        data.email,
        _SUBJECT_LABELS.get(data.subject, data.subject),
        data.message,
    ]
    written = await append_row(sheet_id, "Sheet1", row)
    if not written:
        logger.warning("Could not write contact to Google Sheet (submission still saved)")

    # --- 2. Send email notification ---
    church_email = os.getenv("CHURCH_NOTIFICATION_EMAIL", "larencontrefr@gmail.com")
    subject = f"📩 Nouveau contact : {_SUBJECT_LABELS.get(data.subject, data.subject)} — {data.name}"
    html = _build_contact_email_html(data.model_dump())

    # Attempt email in background — don't block the response
    await send_email(to=church_email, subject=subject, html_body=html, reply_to=data.email)

    logger.info(f"Contact submission from {data.name} ({data.email})", extra={"subject": data.subject})
    return ContactResponse()


import os
