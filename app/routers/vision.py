"""Vision API endpoints."""

from fastapi import APIRouter

from app.models.vision import VisionSection, VisionListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=VisionListResponse)
async def list_vision_sections():
    """List all active vision/mission sections."""
    data = await sheets_service.get_vision()
    
    # Filter to only active sections
    data = [s for s in data if s.get("is_active", "").upper() == "TRUE"]
    
    # Sort by display_order
    data.sort(key=lambda x: int(x.get("display_order", "999") or "999"))
    
    sections = [VisionSection(**section) for section in data]
    return VisionListResponse(sections=sections, total=len(sections))
