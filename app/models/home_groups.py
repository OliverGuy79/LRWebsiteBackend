"""Pydantic models for Home Groups."""

import re
from pydantic import BaseModel, Field, field_validator


def transform_google_drive_url(url: str | None) -> str | None:
    """
    Transform Google Drive sharing URL to proxy URL.

    Supported input formats:
    - https://drive.google.com/file/d/{ID}/view?usp=...
    - https://drive.google.com/open?id={ID}&usp=...

    Output: /api/images/google-drive/{ID}
    """
    if not url:
        return url

    file_id = None

    # Format: /file/d/{ID}/
    pattern1 = r"https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/"
    url_match = re.match(pattern1, url)
    if url_match:
        file_id = url_match.group(1)

    # Format: /open?id={ID}
    if not file_id:
        pattern2 = r"https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)"
        url_match = re.match(pattern2, url)
        if url_match:
            file_id = url_match.group(1)

    if file_id:
        return f"/api/images/google-drive/{file_id}"

    return url


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
    image: str | None = Field(None, validation_alias="image")

    @field_validator("image", mode="before")
    @classmethod
    def transform_image_url(cls, v):
        return transform_google_drive_url(v)

    model_config = {"populate_by_name": True}


class HomeGroupListResponse(BaseModel):
    """Response for listing home groups."""
    home_groups: list[HomeGroup]
    total: int
