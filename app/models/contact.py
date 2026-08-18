"""Pydantic models for Contact submissions."""

from pydantic import BaseModel, EmailStr, Field


class ContactSubmission(BaseModel):
    """Incoming contact form data."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=6, max_length=30)
    subject: str = Field(default="general", max_length=100)
    message: str = Field(..., min_length=5, max_length=5000)


class ContactResponse(BaseModel):
    """Response after successful contact submission."""
    success: bool = True
    message: str = "Message envoyé avec succès"
