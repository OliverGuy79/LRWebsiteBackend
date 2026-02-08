"""Pydantic models for Vision."""

from pydantic import BaseModel


class VisionSection(BaseModel):
    """Vision and mission section."""
    id: str
    section: str | None = None
    title: str
    content: str | None = None
    subtitle: str | None = None
    icon: str | None = None
    image: str | None = None
    display_order: str | None = None
    status: str | None = None  # published, draft, archived (was is_active)
    created_at: str | None = None
    updated_at: str | None = None


class VisionListResponse(BaseModel):
    """Response for listing vision sections."""
    sections: list[VisionSection]
    total: int
