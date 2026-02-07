"""Pydantic models for Events."""

from pydantic import BaseModel


class Event(BaseModel):
    """Church event - matches actual sheet columns."""
    id: str
    title: str
    description: str | None = None
    location: str | None = None
    address: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    image: str | None = None
    category: str | None = None
    registration_required: str | None = None
    registration_link: str | None = None
    is_recurring: str | None = None  # New field from sheet
    recurrence_pattern: str | None = None  # New field from sheet
    status: str | None = None  # Was is_published, now status
    created_at: str | None = None
    updated_at: str | None = None


class EventListResponse(BaseModel):
    """Response for listing events."""
    events: list[Event]
    total: int
