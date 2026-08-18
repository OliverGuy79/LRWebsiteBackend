"""Pydantic models for Boutique reservations."""

from pydantic import BaseModel, Field


class ReservationItem(BaseModel):
    """Product info attached to a reservation."""
    id: str
    name: str
    category: str | None = None


class ReservationRequest(BaseModel):
    """Incoming reservation form data."""
    product: ReservationItem
    name: str = Field(..., min_length=1, max_length=100)
    firstname: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=6, max_length=20)
    quantity: int = Field(default=1, ge=1, le=10)
    size: str | None = None
    color: str | None = None


class ReservationResponse(BaseModel):
    """Response after successful reservation."""
    success: bool = True
    message: str = "Réservation enregistrée avec succès"
