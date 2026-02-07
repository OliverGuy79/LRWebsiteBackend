"""Pydantic models for Church Information."""

from pydantic import BaseModel


class ChurchInfo(BaseModel):
    """Church contact and general information."""
    id: str | None = None
    church_name: str
    slogan: str | None = None
    founded_year: str | None = None
    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    phone: str | None = None
    email: str | None = None
    facebook: str | None = None
    instagram: str | None = None
    twitter: str | None = None
    youtube: str | None = None
    opening_hours: str | None = None
    logo_url: str | None = None
