"""Pydantic models for Pastoral Team."""

from pydantic import BaseModel


class TeamMember(BaseModel):
    """Pastoral team member - matches actual sheet columns."""
    id: str
    first_name: str
    last_name: str
    title: str | None = None
    role: str | None = None
    bio: str | None = None
    photo: str | None = None
    email: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    instagram: str | None = None
    linkedin: str | None = None
    is_senior_pastor: str | None = None
    display_order: str | None = None
    is_active: str | None = None  # Was status, now is_active
    created_at: str | None = None
    updated_at: str | None = None


class TeamListResponse(BaseModel):
    """Response for listing team members."""
    team: list[TeamMember]
    total: int
