"""Pydantic models for Events."""

from pydantic import BaseModel


class Event(BaseModel):
    """Church event."""
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
    is_published: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class EventListResponse(BaseModel):
    """Response for listing events."""
    events: list[Event]
    total: int
