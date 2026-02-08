"""Vision API endpoints."""

from fastapi import APIRouter, Query

from app.models.vision import VisionSection, VisionListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=VisionListResponse)
async def list_vision_sections(
    preview: bool = Query(False, description="Include draft content for preview"),
):
    """List all published vision/mission sections."""
    data = await sheets_service.get_vision()
    
    # Filter by status
    if preview:
        # Show published and draft (not archived)
        data = [s for s in data if s.get("status", "").lower() in ("published", "draft")]
    else:
        # Only show published
        data = [s for s in data if s.get("status", "").lower() == "published"]
    
    # Sort by display_order
    data.sort(key=lambda x: int(x.get("display_order", "999") or "999"))
    
    sections = [VisionSection(**section) for section in data]
    return VisionListResponse(sections=sections, total=len(sections))
