"""Boutique API endpoints — including reservations."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.models.boutique import Product, ProductListResponse
from app.models.reservation import ReservationRequest, ReservationResponse
from app.services import sheets_service
from app.services.sheets_write_service import append_row
from app.services.email_service import send_email
from app.services.email_templates import build_reservation_email
from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Products (read from Google Sheet)
# ---------------------------------------------------------------------------

@router.get("", response_model=ProductListResponse)
async def list_products(
    category: str | None = Query(None, description="Filter by category"),
    in_stock: bool | None = Query(None, description="Filter by stock status"),
    preview: bool = Query(False, description="Include draft content for preview"),
):
    """List all published products."""
    data = await sheets_service.get_boutique()

    if preview:
        data = [p for p in data if p.get("status", "").lower() in ("published", "draft")]
    else:
        data = [p for p in data if p.get("status", "").lower() == "published"]

    if category:
        data = [p for p in data if p.get("category", "").lower() == category.lower()]

    if in_stock is not None:
        stock_value = "TRUE" if in_stock else "FALSE"
        data = [p for p in data if p.get("is_in_stock", "").upper() == stock_value]

    products = [Product(**product) for product in data]
    return ProductListResponse(products=products, total=len(products))


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    preview: bool = Query(False, description="Allow viewing draft products"),
):
    """Get a single product by ID."""
    data = await sheets_service.get_boutique()

    product_data = next((p for p in data if p.get("id") == product_id), None)

    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")

    status = product_data.get("status", "").lower()
    if not preview and status != "published":
        raise HTTPException(status_code=404, detail="Product not found")

    return Product(**product_data)


# ---------------------------------------------------------------------------
# Reservations (write to Google Sheet)
# ---------------------------------------------------------------------------

@router.post("/reservations", response_model=ReservationResponse, status_code=201)
async def create_reservation(data: ReservationRequest):
    """
    Handle a boutique reservation:
      1. Save to the Google Sheet (SHEET_ID_RESERVATIONS)
      2. Send notification email
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # --- 1. Write to Google Sheet ---
    sheet_id = settings.sheet_id_reservations or settings.sheet_id_boutique
    sheet_name = settings.sheet_name_reservations
    row = [
        timestamp,
        data.name,
        data.firstname,
        data.phone,
        data.product.id,
        data.product.name,
        data.product.category or "",
        data.size or "",
        data.color or "",
        str(data.quantity),
    ]
    written = await append_row(sheet_id, sheet_name, row)
    if not written:
        logger.error("Could not write reservation to Google Sheet")
        raise HTTPException(
            status_code=503,
            detail="La réservation n’a pas pu être enregistrée. Veuillez réessayer.",
        )

    # --- 2. Send email notification ---
    recipients = await sheets_service.get_notification_recipients()
    payload = data.model_dump()
    subject = f"🛍️ Réservation boutique : {data.product.name} — {data.name} {data.firstname}"
    html = build_reservation_email(payload)
    email_results = [
        await send_email(to=recipient, subject=subject, html_body=html)
        for recipient in recipients
    ]
    if not all(email_results):
        logger.warning("One or more reservation notification emails could not be sent", extra={
            "recipient_count": len(recipients),
            "failed_count": email_results.count(False),
        })

    logger.info(f"Reservation for {data.product.name} by {data.name} {data.firstname}")
    return ReservationResponse()
