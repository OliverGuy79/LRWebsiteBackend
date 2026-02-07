"""Pydantic models for Home Groups."""

from pydantic import BaseModel, Field


class HomeGroup(BaseModel):
    """
    Small group / home group.
    
    Note: The sheet uses French column names. We use Field validation_alias
    to parse French columns but serialize with English field names.
    """
    # Actual sheet columns (header row):
    # id, HOME, Leader(s), Description de la home (2 phrases max), 
    # Jour et Horaires, Fréquence, Date de la 1ere rencontre, Taille de teeshirt
    
    id: int | None = Field(None, validation_alias="id")
    home: str | None = Field(None, validation_alias="HOME")
    leaders: str | None = Field(None, validation_alias="Leader(s)")
    description: str | None = Field(None, validation_alias="Description de la home (2 phrases max)")
    schedule: str | None = Field(None, validation_alias="Jour et Horaires")
    frequency: str | None = Field(None, validation_alias="Fréquence")
    first_meeting_date: str | None = Field(None, validation_alias="Date de la 1ere rencontre")
    tshirt_size: str | None = Field(None, validation_alias="Taille de teeshirt")
    
    model_config = {"populate_by_name": True}


class HomeGroupListResponse(BaseModel):
    """Response for listing home groups."""
    home_groups: list[HomeGroup]
    total: int
