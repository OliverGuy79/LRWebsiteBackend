"""Pydantic models for Home Groups."""

from pydantic import BaseModel


class HomeGroup(BaseModel):
    """Small group / home group."""
    id: str | None = None
    name: str | None = None
    leader: str | None = None
    co_leader: str | None = None
    location: str | None = None
    address: str | None = None
    day_of_week: str | None = None
    time: str | None = None
    description: str | None = None
    category: str | None = None
    max_capacity: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    image: str | None = None
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class HomeGroupListResponse(BaseModel):
    """Response for listing home groups."""
    home_groups: list[HomeGroup]
    total: int
