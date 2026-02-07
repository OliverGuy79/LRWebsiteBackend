"""Pydantic models for Vision content."""

from pydantic import BaseModel


class VisionSection(BaseModel):
    """Vision/mission section."""
    id: str
    section: str | None = None
    title: str | None = None
    content: str | None = None
    subtitle: str | None = None
    icon: str | None = None
    image: str | None = None
    display_order: str | None = None
    is_active: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class VisionListResponse(BaseModel):
    """Response for listing vision sections."""
    sections: list[VisionSection]
    total: int
