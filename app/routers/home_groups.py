"""Home Groups API endpoints."""

from fastapi import APIRouter, Query

from app.models.home_groups import HomeGroup, HomeGroupListResponse
from app.services import sheets_service


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
    
    # Filter by frequency if provided
    if frequency:
        data = [g for g in data if frequency.lower() in g.get("Fréquence", "").lower()]
    
    # Parse using aliases (French column names) - output will use English field names
    groups = [HomeGroup.model_validate(group) for group in data]
    
    return HomeGroupListResponse(home_groups=groups, total=len(groups))
