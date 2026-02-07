"""Pydantic models for Home Groups."""

from pydantic import BaseModel, Field


class HomeGroup(BaseModel):
    """
    Small group / home group.
    
    Note: The sheet uses French column names. We use Field aliases
    to map them to English model field names.
    """
    # Actual sheet columns (header row when filter is removed):
    # HOME, Leader(s), Description de la home (2 phrases max), 
    # Jour et Horaires, Fréquence, Date de la 1ere rencontre, Taille de teeshirt
    id: int | None = Field(None, alias="id")
    home: str | None = Field(None, alias="HOME")
    leaders: str | None = Field(None, alias="Leader(s)")
    description: str | None = Field(None, alias="Description de la home (2 phrases max)")
    schedule: str | None = Field(None, alias="Jour et Horaires")
    frequency: str | None = Field(None, alias="Fréquence")
    first_meeting_date: str | None = Field(None, alias="Date de la 1ere rencontre")
    tshirt_size: str | None = Field(None, alias="Taille de teeshirt")
    
    model_config = {"populate_by_name": True}


class HomeGroupListResponse(BaseModel):
    """Response for listing home groups."""
    home_groups: list[HomeGroup]
    total: int
