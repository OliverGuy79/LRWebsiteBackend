"""Pydantic models for Services."""

from pydantic import BaseModel


class Service(BaseModel):
    """Church service times."""
    id: str
    name: str
    description: str | None = None
    day_of_week: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    location: str | None = None
    leaders: str | None = None
    service_type: str | None = None
    language: str | None = None
    has_childcare: str | None = None
    image: str | None = None
    display_order: str | None = None
    status: str | None = None  # published, draft, archived (was is_active)
    created_at: str | None = None
    updated_at: str | None = None


class ServiceListResponse(BaseModel):
    """Response for listing services."""
    services: list[Service]
    total: int
