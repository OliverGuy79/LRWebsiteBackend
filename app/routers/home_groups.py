"""Home Groups API endpoints."""

from fastapi import APIRouter, Query

from app.models.home_groups import HomeGroup, HomeGroupListResponse
from app.services import sheets_service


router = APIRouter()


@router.get("", response_model=HomeGroupListResponse)
async def list_home_groups(
    day: str | None = Query(None, description="Filter by day of week"),
    category: str | None = Query(None, description="Filter by category"),
):
    """List all active home groups."""
    data = await sheets_service.get_home_groups()
    
    # Filter to only active groups
    data = [g for g in data if g.get("status", "").lower() == "active"]
    
    # Filter by day if provided
    if day:
        data = [g for g in data if g.get("day_of_week", "").lower() == day.lower()]
    
    # Filter by category if provided
    if category:
        data = [g for g in data if g.get("category", "").lower() == category.lower()]
    
    groups = [HomeGroup(**group) for group in data]
    return HomeGroupListResponse(home_groups=groups, total=len(groups))
