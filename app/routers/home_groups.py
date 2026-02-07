"""Home Groups API endpoints."""

from fastapi import APIRouter, Query

from app.models.home_groups import HomeGroup, HomeGroupListResponse
from app.services import sheets_service

import logging


router = APIRouter()


@router.get("", response_model=HomeGroupListResponse)
async def list_home_groups(
    frequency: str | None = Query(None, description="Filter by frequency (e.g., '1 fois par mois')"),
):
    """
    List all home groups.
    
    Note: The sheet uses French column names which are mapped to English model fields.
    Response uses English field names (home, leaders, schedule, etc.)
    """
    data = await sheets_service.get_home_groups()
    
    # Filter by day if provided
    if day:
        data = [g for g in data if g.get("day_of_week", "").lower() == day.lower()]
    
    # Filter by category if provided
    if category:
        data = [g for g in data if g.get("category", "").lower() == category.lower()]

    
    groups = [HomeGroup(**group) for group in data]
    return HomeGroupListResponse(home_groups=groups, total=len(groups))
