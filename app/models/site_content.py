"""Pydantic models for Site Content."""

from pydantic import BaseModel


class SiteContentItem(BaseModel):
    """A single site content entry keyed by a unique string."""
    id: str
    key: str
    content: str | None = None


class SiteContentResponse(BaseModel):
    """Response for listing site content."""
    items: list[SiteContentItem]
    total: int
