"""Church Info API endpoints."""

from fastapi import APIRouter

from app.models.church_info import ChurchInfo
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=ChurchInfo)
async def get_church_info():
    """
    Get church information (first row from sheet).
    
    Returns contact details, social media links, and general info.
    """
    data = await sheets_service.get_church_info()
    
    if not data:
        return ChurchInfo(church_name="Église LaRencontre")
    
    # Return first row (should only be one row of church info)
    return ChurchInfo(**data[0])
